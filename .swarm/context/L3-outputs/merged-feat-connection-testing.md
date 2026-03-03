# Merged — feat-connection-testing

**Extracted**: 2026-03-02T16:17:43Z
**Issue**: #41
**PR**: #43 — feat: implement data source connection testing
**Agent**: claude (claude-sonnet-4-20250514)
**Type**: feature
**Attempt**: 1 (one-shot: yes)
**Total Time**: 5m

## Prompt Used
```markdown
## Task
Implement actual data source connection testing in `api/routers/sources.py`.

## Context
The `POST /api/sources/{source_id}/test` endpoint currently returns a hardcoded success. There's a TODO at line ~88. You need to wire it up to the actual connectors.

## Key Files
- `api/routers/sources.py` — the router to modify (the `test_connection` endpoint)
- `connectors/base.py` — base connector class with `connect()` method
- `connectors/sqlite.py` — simplest connector, use for testing
- `connectors/__init__.py` — connector registry/factory
- `api/schemas/sources.py` — existing schemas
- `tests/test_api_sources.py` — add tests here

## Requirements
1. In the `test_connection` endpoint, look up the source from the DB
2. Based on `source.type`, instantiate the correct connector from `connectors/`
3. Try calling `connect()` (or equivalent) on the connector
4. Return `{"success": true, "message": "..."}` on success
5. Return `{"success": false, "error": "..."}` on connection failure (HTTP 200, not 500)
6. Return 404 if source not found
7. Handle unsupported source types gracefully

## Testing
Write at least 2 new tests in `tests/test_api_sources.py`:
- Test connection with a valid SQLite source
- Test connection with a non-existent source (404)

Run:
```bash
source .venv/bin/activate && python -m pytest tests/test_api_sources.py -v 2>&1 | tail -15
```

## Constraints
- Don't install new dependencies — use only what's in requirements.txt
- Keep it simple — this is a connection TEST, not a full data pipeline
- Handle errors gracefully (try/except around connector calls)

## Git Operations (YOU must do all of these)
1. Implement the feature
2. Write tests
3. Run tests and verify they pass
4. `git add -A && git commit -m "feat: implement data source connection testing"`
5. `git push origin feat/connection-testing`
6. `gh pr create --title "feat: implement data source connection testing" --body "Closes #41" --base main --head feat/connection-testing --repo xdatahubai-a11y/dataquality-platform`

Do NOT stop until the PR is created.
```

## Files Changed
api/routers/sources.py
api/schemas/sources.py
connectors/__init__.py
tests/test_api_sources.py

## PR Description
## Summary
Implements actual data source connection testing in the `POST /api/sources/{source_id}/test` endpoint, replacing the hardcoded TODO response.

### Changes Made
- ✅ **Connection Testing Logic**: Added real connector-based testing in `api/routers/sources.py`
- ✅ **Connector Factory**: Created `get_connector()` factory function in `connectors/__init__.py`
- ✅ **Schema Updates**: Added SQLite and BigQuery to allowed source types
- ✅ **Error Handling**: Proper exception handling for connection failures
- ✅ **Structured Responses**: Returns `{"success": boolean, "message/error": string}` format
- ✅ **Comprehensive Tests**: Added 5 new test cases covering various scenarios

### API Response Format
**Success**: `{"success": true, "message": "Successfully connected to [source_name]"}`
**Failure**: `{"success": false, "error": "[error_description]"}` 
**404**: Standard HTTP 404 for non-existent sources

### Test Coverage
- ✅ Valid SQLite connection test
- ✅ Invalid SQLite database path handling
- ✅ Non-existent source (404) handling
- ✅ Missing configuration error handling
- ✅ Backwards compatibility with existing test

### Implementation Details
- Uses the existing connector architecture from `connectors/` directory
- Handles all connector types through the factory pattern
- Properly closes connections after testing
- Graceful error handling without 500 responses
- Maintains backwards compatibility

Closes #41

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## AI Review Findings
(no AI reviews found)

## Tags
- type:feature
- agent:claude
- one-shot:yes
- issue:41
