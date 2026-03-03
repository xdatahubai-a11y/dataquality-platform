# Merged — fix-cors-health

**Extracted**: 2026-03-02T16:17:34Z
**Issue**: #46
**PR**: #49 — fix: configurable CORS origins and enhanced health endpoint
**Agent**: claude (claude-sonnet-4-20250514)
**Type**: bugfix
**Attempt**: 1 (one-shot: yes)
**Total Time**: 3m

## Prompt Used
```markdown
## Task
Make CORS origins configurable from environment and enhance the health endpoint.

## Key Files
- `api/main.py` — CORS middleware + health endpoint
- `api/config.py` — Settings class (pydantic-settings, reads from env)
- `api/dependencies.py` — database engine/session
- `pyproject.toml` — has version "0.1.0"

## Requirements

### 1. CORS from environment
- Add `cors_origins: str = "*"` to Settings in `api/config.py`
- In `api/main.py`, parse it: split by comma, strip whitespace
- Default `"*"` keeps backward compatibility

### 2. Dynamic version
- Read version from `importlib.metadata.version("dataquality-platform")` with fallback to env var `APP_VERSION` or `"dev"`
- Add to Settings or read directly in health endpoint

### 3. Enhanced health endpoint
Return:
```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"  // or "error: <message>"
}
```
Test DB connectivity by running a simple `SELECT 1` query.

### 4. Tests
Add `tests/test_health.py`:
- Health returns 200 with version and database status
- Health returns database connected status

Run: `source .venv/bin/activate && python -m pytest tests/test_health.py tests/test_api_rules.py -v`

## Git Operations
1. Implement changes
2. Write tests
3. Run tests
4. `git add -A && git commit -m "fix: configurable CORS origins and enhanced health endpoint"`
5. `git push origin fix/cors-health`
6. `gh pr create --title "fix: configurable CORS origins and enhanced health endpoint" --body "Closes #46" --base main --head fix/cors-health --repo xdatahubai-a11y/dataquality-platform`

Do NOT stop until the PR is created.
```

## Files Changed
api/config.py
api/main.py
tests/test_health.py

## PR Description
## Summary

This PR implements configurable CORS origins and enhances the health endpoint to provide more comprehensive system status information.

### Changes Made

- **Configurable CORS Origins**: Added `cors_origins` setting to config with default "*" for backward compatibility
  - Environment variable: `DQ_CORS_ORIGINS` (comma-separated list)
  - Automatically strips whitespace from origins
  
- **Dynamic Version Management**: 
  - Reads version from package metadata using `importlib.metadata.version()`
  - Falls back to `APP_VERSION` environment variable or "dev"
  - Updates FastAPI app version to use dynamic version

- **Enhanced Health Endpoint**: 
  - Returns version information
  - Tests database connectivity with `SELECT 1` query
  - Provides detailed database status ("connected" or "error: <message>")

- **Comprehensive Tests**: Added `tests/test_health.py` with full coverage:
  - Health endpoint returns 200 status
  - Correct JSON structure validation
  - Version field validation
  - Database connectivity testing
  - Database error handling

### API Response Format

```json
{
  "status": "healthy",
  "version": "0.1.0",
  "database": "connected"
}
```

### Environment Variables

- `DQ_CORS_ORIGINS`: Comma-separated list of allowed origins (default: "*")
- `APP_VERSION`: Fallback version when package metadata unavailable (default: "dev")

### Testing

✅ All existing tests pass  
✅ New health endpoint tests added  
✅ Manual testing of CORS configuration  
✅ Manual testing of health endpoint functionality  

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## AI Review Findings
(no AI reviews found)

## Tags
- type:bugfix
- agent:claude
- one-shot:yes
- issue:46
