# Evidence scope

- observations.json is a curated summary derived from actual recorded runs, not a raw execution log.
- red-unit.log contains the nine actual test-status lines and final summary from the original-code run. Tracebacks and machine-specific paths were omitted.
- green-unit.log is the recorded final formatted-suite unittest stderr, with line endings normalized.
- The baseline and first green run used identical test bytes; the formatted suite was run again.
- changes.patch contains the local application fix, tests, test entry point, and documentation, relative to the assessed source.
- No load test, exhaustion threshold, real LLM, production deployment, or security boundary crossing is represented.

The public bundle intentionally excludes workstation-specific full runner metadata and raw traceback paths. No measured outcome has been replaced by expected output.
