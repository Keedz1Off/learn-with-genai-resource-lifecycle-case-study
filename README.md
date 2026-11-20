# Learn with GenAI resource cleanup

Two chat requests completed but left SQLite connections and workers running. The local cleanup fix improved the original test suite from **1 of 9 passing to 9 of 9 passing**.

The next ordinary chat request still worked in the baseline test. The result covers resource cleanup in this application, and the fix was verified locally.

## Evidence

- [Recorded observations](evidence/observations.json)
- [Before the fix](evidence/red-unit.log) · [After the fix](evidence/green-unit.log)
- [Original lifecycle tests](regression/test_ai_tutor_connection_lifecycle.py)
- [Boundary matrix index](matrices/boundaries.json) · [HTTP lifecycle](matrices/HTTP-LIFECYCLE.json) · [Workflow lifecycle](matrices/WORKFLOW-LIFECYCLE.json)

## Run the checks

[Open Case study checks in GitHub Actions](https://github.com/Keedz1Off/learn-with-genai-resource-lifecycle-case-study/actions/workflows/checks.yml) and select **Run workflow**. CI runs two offline tests. They check the saved lifecycle results and the checksum of the original regression test file.

The run saves `check-results`. Select **CD demo** to also package the passing log, commit SHA and checksum as `verified-delivery`.

Run locally with Python 3.10 or later:

```sh
python -B -m unittest discover -s tests -v
```
