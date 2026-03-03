# Issue #41: feat: implement data source connection testing

**Ingested**: 2026-03-02T16:18:04Z
**Created**: 2026-03-02T06:52:28Z
**Labels**: agent:claude, type:feature, status:ready-for-human, complexity:medium, attempt:1, priority:medium

## Body
Implement actual connection testing in api/routers/sources.py (line 88 TODO).
Use connectors/ to test real connections. Handle 404, 422, and connection failure.
Key files: api/routers/sources.py, connectors/base.py, connectors/sqlite.py, tests/test_api_sources.py
Verify: source .venv/bin/activate && python -m pytest tests/test_api_sources.py -v

## Comments

