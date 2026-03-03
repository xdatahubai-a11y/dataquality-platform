# Issue #44: feat: implement local DQ job execution in jobs router

**Ingested**: 2026-03-02T16:18:02Z
**Created**: 2026-03-02T07:42:51Z
**Labels**: priority:high, agent:claude, type:feature, status:ready-for-human, complexity:medium, attempt:1

## Body
## Problem
The `POST /api/jobs` endpoint creates a job record but never actually runs the DQ checks (line 32: `# TODO: Dispatch to Spark via spark/submit.py`).

## Requirements
Implement **synchronous local execution** (not Spark) for submitted jobs:

1. After creating the DQRun record, load the rules referenced in `job.rule_ids` from the DB
2. Load the source config from `job.source_id`
3. Use the appropriate connector to read data from the source
4. Run rules through `engine.rule_engine.run_checks()`
5. Store results in the `DQMetric` table (one row per rule result)
6. Update the DQRun status to `completed` (or `failed` on error)
7. Set `completed_at` timestamp

## Key Files (must read/understand all)
- `api/routers/jobs.py` — the router (main changes here)
- `api/models/database.py` — DQRun, DQMetric, DQRule, DataSource models
- `api/schemas/jobs.py` — request/response schemas
- `engine/rule_engine.py` — `evaluate_rule()`, `RuleDefinition`, `run_checks()`
- `connectors/__init__.py` — `get_connector(source_type)`
- `connectors/sqlite.py` — simplest connector for testing

## Testing
Add tests in a new file `tests/test_job_execution.py`:
- Submit job with SQLite source + completeness rule → verify status=completed, metrics stored
- Submit job with invalid source_id → verify status=failed
- Submit job with no matching rules → verify graceful handling

Run: `source .venv/bin/activate && python -m pytest tests/test_job_execution.py -v`

## Constraints
- Use LOCAL execution only (`spark.submit.submit_local` or direct `run_checks()`)
- Do NOT block the API — run synchronously for now (async is a future task)
- Handle errors gracefully: if execution fails, update status to `failed` with error in parameters
- Don't break existing tests

## Comments

