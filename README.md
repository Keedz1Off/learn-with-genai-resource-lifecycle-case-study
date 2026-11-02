# Learn with GenAI: chat ended, SQLite resources stayed open

**Status:** application lifecycle bug; local fix verified. Exploitable DoS not established.

The chat endpoint runs a LangGraph workflow with SQLite checkpoints.

- **Expected:** finish the response, close its iterators, release the connection and worker.
- **Observed:** two ordinary chats finished but left two connections and worker threads alive.
- **Impact:** unused resources remained allocated. The next request still worked; exhaustion, an outage and data disclosure were not demonstrated.
- **Local fix:** scope the connection with `async with` and close iterators in ownership order. The same nine tests changed from **1 pass / 8 failures** to **9 passes**. Not submitted or merged upstream.

This is an application bug, not a demonstrated LangGraph library vulnerability.

**Flow:** HTTP chat → workflow → SQLite checkpoint connection → response and cleanup.

## Matrices

| Boundary | JSON |
| --- | --- |
| Iterator and connection lifecycle | [WORKFLOW-LIFECYCLE](matrices/WORKFLOW-LIFECYCLE.json) |
| HTTP completion and retained resources | [HTTP-LIFECYCLE](matrices/HTTP-LIFECYCLE.json) |

Read each row as: **invariant → scenario → oracle → observation → status → evidence → limit**.

[Detailed report, tests, logs and source pins](https://github.com/Keedz1Off/learn-with-genai-resource-lifecycle-case-study/tree/59ea74ee36db31da912d2afbe49af924fcb83cdc) are preserved in the pinned evidence snapshot. Matrix links open the exact supporting records.

Learn with GenAI v0.1.1, 8372d4a; local deterministic model. Independent, AI-assisted work. Documentation reorganisation only; no new target tests. [File inventory](package-manifest.json).
