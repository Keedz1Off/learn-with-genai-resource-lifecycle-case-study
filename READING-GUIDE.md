# Learn with GenAI: reading guide

## Two-minute route

[README](README.md) → [FLOW.md](FLOW.md) → the before/after counts in [observations.json](evidence/observations.json).

The case is straightforward: a chat response finished while its SQLite connection and worker thread stayed alive. A local cleanup patch released the resources in the recorded scenarios.

## File map

| File | What to inspect |
| --- | --- |
| [README.md](README.md) | Result, scope, expected vs observed behavior and impact limits. |
| [FLOW.md](FLOW.md) | HTTP route, workflow, saver, connection ownership and cleanup order. |
| [changes.patch](changes.patch) | Application fix, regression tests and test entry point; apply to the assessed upstream snapshot. |
| [evidence/observations.json](evidence/observations.json) | Source pins, environment, HTTP measurements, nine test cases and limitations. |
| [evidence/red-unit.log](evidence/red-unit.log) | Original-code result: 1 pass and 8 failures. |
| [evidence/green-unit.log](evidence/green-unit.log) | Recorded final patched-suite result: 9 passes. |
| [evidence/requirements.txt](evidence/requirements.txt) | Recorded dependency versions for the local checks. |
| [evidence/README.md](evidence/README.md) | Which records are curated summaries and which are retained test-status lines. |
| [LICENSE-UPSTREAM.txt](LICENSE-UPSTREAM.txt) | License for included upstream-derived patch code. |

## How to read the patch

1. Find the workflow connection allocation and its ownership scope.
2. Follow graph-iterator closure before connection release.
3. Inspect the response wrapper's workflow-iterator cleanup.
4. Read the assertions in the added tests. Distinguish the expected close from cleanup forced by the fixture.
5. Compare original and patched results from the same regression scenarios.

The test source is included in `changes.patch`; it is not a standalone runnable suite at this repository's root. The replay command and assessed snapshot are in [README.md](README.md).

## Explain it in one minute

- **Expected:** finish or stop a stream, close its iterator, release its owned connection.
- **Observed:** original ordinary requests finished with connections and workers retained.
- **Fix:** make ownership explicit and close resources in the correct order.
- **Evidence:** before/after HTTP observations and nine regression tests.
- **Classification:** confirmed application lifecycle bug; availability risk is conditional, and exploitable DoS is not established.

The patch is local, not a claimed merged or shipped upstream fix. This navigation update adds no new target-test results.
