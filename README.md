# Learn with GenAI: chat ended, SQLite resources stayed open

**Status:** application lifecycle bug; local fix verified. Exploitable DoS not established.

The chat endpoint runs a LangGraph workflow with SQLite checkpoints.

- **Expected:** finish the response, close its iterators, release the connection and worker.
- **Observed:** two ordinary chats finished but left two connections and worker threads alive.
- **Impact:** unused resources remained allocated. The next request still worked; exhaustion, an outage and data disclosure were not demonstrated.
- **Local fix:** scope the connection with `async with` and close iterators in ownership order. The same nine tests changed from **1 pass / 8 failures** to **9 passes**. Not submitted or merged upstream.

This is an application bug, not a demonstrated LangGraph library vulnerability.

## Evidence and details

[Boundary matrix](matrices/boundaries.json) · [Flow](FLOW.md) · [Patch and tests](changes.patch) · [Before log](evidence/red-unit.log) · [After log](evidence/green-unit.log) · [Measurements](evidence/observations.json)

Assessed: `vandenn/learn-with-genai` v0.1.1, `8372d4a`; AI-assisted local testing with a deterministic model. [Technical details](CASE-STUDY.md) · [File map](READING-GUIDE.md) · [Upstream report](https://github.com/vandenn/learn-with-genai/issues/19).

Historical results; no new target execution in this documentation edit.
