# Issue #46: refactor: add CORS configuration from environment and secure health endpoint

**Ingested**: 2026-03-02T16:22:45Z
**Created**: 2026-03-02T07:42:55Z
**Labels**: priority:high, agent:claude, type:bugfix, complexity:small, status:ready-for-human, attempt:1

## Body
## Problem
`api/main.py` has `allow_origins=["*"]` hardcoded — this is a security issue for any real deployment. Also the health endpoint returns a hardcoded version string.

## Requirements
1. Read CORS origins from environment variable `CORS_ORIGINS` (comma-separated), default to `["*"]` for dev
2. Read app version from `pyproject.toml` or environment variable `APP_VERSION`
3. Health endpoint should return: version (dynamic), uptime, database connectivity status
4. Add the CORS and version settings to `api/config.py` (the Settings class)

## Key Files
- `api/main.py` — CORS middleware + health endpoint
- `api/config.py` — Settings class (pydantic-settings)
- `api/dependencies.py` — database engine
- `tests/test_api_rules.py` — health test if any

## Testing
- Health endpoint returns dynamic version
- Health endpoint returns db status
- CORS respects env var when set

Run: `source .venv/bin/activate && python -m pytest tests/ -k health -v`

## Constraints
- Don't break existing tests
- Keep backward compatible — default CORS is still '*' for dev

## Comments

