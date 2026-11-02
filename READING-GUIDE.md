# Reading guide

Start with [README](README.md) for the bug, impact and fix.

| Next question | File |
| --- | --- |
| Who owns the connection, and what must close first? | [FLOW.md](FLOW.md) |
| Which scenarios were checked? | [Boundary matrix](matrices/boundaries.json) |
| What code changed? | [changes.patch](changes.patch) — includes the tests |
| What failed before and passed after? | [Before log](evidence/red-unit.log) and [after log](evidence/green-unit.log) |
| What did the HTTP checks measure? | [observations.json](evidence/observations.json) |
| How can I reproduce the local tests? | [CASE-STUDY.md](CASE-STUDY.md) and [requirements.txt](evidence/requirements.txt) |
| What are the evidence and license terms? | [Evidence notes](evidence/README.md) and [upstream license](LICENSE-UPSTREAM.txt) |

Apply the patch to the assessed upstream snapshot before running its tests. This repository is a case-study package, not the complete application.
