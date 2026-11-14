import asyncio
import os
import socket
import tempfile
import unittest
from contextlib import suppress
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

import aiosqlite

from src.logic.ai_tutor.graphs import main as workflow
from src.v1.routes import ai_tutor as chat_route
from src.v1.schema import AITutorChatRequest


class ConnectionLifecycleTests(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.directory = tempfile.TemporaryDirectory(
            prefix="tutor-ownership-", dir=os.environ.get("LWG_TEST_TMPDIR")
        )
        self.addCleanup(self.directory.cleanup)
        self.connections = []
        self.close_counts = {}
        self.events = []
        self.streams = []
        self.tasks = []
        real_connect = aiosqlite.connect
        real_close = aiosqlite.Connection.close

        def connect(*args, **kwargs):
            connection = real_connect(*args, **kwargs)
            self.connections.append(connection)
            self.close_counts[id(connection)] = 0
            return connection

        async def close(connection):
            self.events.append("connection close")
            self.close_counts[id(connection)] += 1
            await real_close(connection)

        async def analyze(_state):
            return {
                "query_type": "GENERAL",
                "output_messages": [{"type": "step", "content": "ready"}],
            }

        async def respond(_state):
            return {"output_messages": [{"type": "final", "content": "answer"}]}

        async def generate_note(_state):
            return {"pending_note_edit": "test note", "output_messages": []}

        replacements = (
            patch.object(
                workflow,
                "settings",
                SimpleNamespace(data_path=Path(self.directory.name)),
            ),
            patch.object(aiosqlite, "connect", connect),
            patch.object(aiosqlite.Connection, "close", close),
            patch.object(workflow, "analyze_user_query", analyze),
            patch.object(workflow, "generate_final_response", respond),
            patch.object(workflow, "generate_note_content", generate_note),
            patch.object(
                socket.socket,
                "connect",
                side_effect=AssertionError("Network is disabled in lifecycle tests"),
            ),
            patch.object(
                socket.socket,
                "connect_ex",
                side_effect=AssertionError("Network is disabled in lifecycle tests"),
            ),
        )
        for replacement in replacements:
            replacement.start()
            self.addCleanup(replacement.stop)

    async def asyncTearDown(self):
        # A failing regression assertion must not leave the original buggy worker alive.
        for task in self.tasks:
            if not task.done():
                task.cancel()
        await asyncio.gather(*self.tasks, return_exceptions=True)
        for stream in self.streams:
            with suppress(Exception, asyncio.CancelledError):
                await stream.aclose()
        for connection in self.connections:
            await connection.close()
            await asyncio.to_thread(connection.join, 2)
            self.assertFalse(connection.is_alive(), "Fixture worker failed to stop")

    def stream(self, **overrides):
        arguments = {
            "user_message": "ordinary question",
            "project_id": "test-project",
            "thread_id": "test-thread",
        }
        arguments.update(overrides)
        stream = workflow.stream_ai_tutor_workflow(**arguments)
        self.streams.append(stream)
        return stream

    async def assert_released(self, index=0):
        connection = self.connections[index]
        self.assertEqual(self.close_counts[id(connection)], 1)
        with self.assertRaisesRegex(ValueError, "no active connection"):
            await connection.execute("SELECT 1")
        await asyncio.to_thread(connection.join, 2)
        self.assertFalse(connection.is_alive())

    async def test_normal_completion_releases_connection(self):
        messages = [message async for message in self.stream()]
        self.assertEqual(
            messages,
            [
                {"type": "step", "content": "ready"},
                {"type": "final", "content": "answer"},
            ],
        )
        self.assertEqual(len(self.connections), 1)
        await self.assert_released()

    async def test_explicit_stream_close_releases_connection(self):
        stream = self.stream()
        self.assertEqual(await anext(stream), {"type": "step", "content": "ready"})
        await stream.aclose()
        await self.assert_released()

    async def test_node_error_releases_connection(self):
        async def fail(_state):
            raise RuntimeError("test node failure")

        with patch.object(workflow, "generate_final_response", fail):
            with self.assertRaisesRegex(RuntimeError, "test node failure"):
                _ = [message async for message in self.stream()]
        await self.assert_released()

    async def test_cancellation_releases_connection(self):
        entered = asyncio.Event()

        async def wait_for_cancellation(_state):
            entered.set()
            await asyncio.Event().wait()

        async def consume():
            return [message async for message in self.stream()]

        with patch.object(workflow, "generate_final_response", wait_for_cancellation):
            task = asyncio.create_task(consume())
            self.tasks.append(task)
            await asyncio.wait_for(entered.wait(), timeout=2)
            task.cancel()
            with self.assertRaises(asyncio.CancelledError):
                await task
        await self.assert_released()

    async def test_compile_error_releases_allocated_connection(self):
        builder = Mock()
        builder.compile.side_effect = RuntimeError("test compile failure")
        with patch.object(workflow, "create_tutor_graph_builder", return_value=builder):
            with self.assertRaisesRegex(RuntimeError, "test compile failure"):
                _ = [message async for message in self.stream()]
        await self.assert_released()

    async def test_builder_error_does_not_allocate_connection(self):
        with patch.object(
            workflow,
            "create_tutor_graph_builder",
            side_effect=RuntimeError("test builder failure"),
        ):
            with self.assertRaisesRegex(RuntimeError, "test builder failure"):
                _ = [message async for message in self.stream()]
        self.assertEqual(self.connections, [])

    async def test_inner_stream_closes_before_connection(self):
        async def steps():
            try:
                yield {
                    "test_node": {
                        "output_messages": [{"type": "step", "content": "ready"}]
                    }
                }
            finally:
                self.events.append("stream close")

        inner = steps()
        self.streams.append(inner)
        graph = Mock()
        graph.astream.return_value = inner
        builder = Mock()
        builder.compile.return_value = graph
        with patch.object(workflow, "create_tutor_graph_builder", return_value=builder):
            stream = self.stream()
            await anext(stream)
            await stream.aclose()
        self.assertEqual(self.events, ["stream close", "connection close"])
        await self.assert_released()

    async def test_response_iterator_close_closes_workflow(self):
        real_workflow = chat_route.stream_ai_tutor_workflow

        def keep_workflow(*args, **kwargs):
            inner = real_workflow(*args, **kwargs)
            self.streams.append(inner)
            return inner

        with (
            patch.object(chat_route, "get_active_file_name", return_value=None),
            patch.object(chat_route, "stream_ai_tutor_workflow", keep_workflow),
        ):
            response = await chat_route.chat(
                AITutorChatRequest(
                    message="ordinary question", project_id="test-project"
                )
            )
            body = response.body_iterator
            self.streams.append(body)
            self.assertIn("data: ", await anext(body))
            await body.aclose()
        await self.assert_released()

    async def test_interrupt_can_resume_after_connection_is_closed(self):
        async def request_note(_state):
            return {"query_type": "ADD_TO_NOTE", "output_messages": []}

        with patch.object(workflow, "analyze_user_query", request_note):
            messages = [message async for message in self.stream()]
        self.assertTrue(any(message["type"] == "consent" for message in messages))
        await self.assert_released()

        resumed = [
            message async for message in self.stream(hitl_input={"content": "approve"})
        ]
        self.assertIn({"type": "note", "content": "test note"}, resumed)
        self.assertIn(
            {"type": "final", "content": "Successfully edited note!"}, resumed
        )
        self.assertEqual(len(self.connections), 2)
        await self.assert_released(1)


if __name__ == "__main__":
    unittest.main()
