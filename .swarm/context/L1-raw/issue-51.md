# Issue #51: feat: add pagination to rules list endpoint

**Ingested**: 2026-03-03T02:29:00Z
**Created**: 2026-03-03T02:28:55Z
**Labels**: status:backlog, priority:normal, type:feature, complexity:small

## Body
## Problem
The `GET /api/rules` endpoint returns all rules at once. This will not scale when there are hundreds of rules.

## Requirements
1. Add `skip` and `limit` query parameters to `GET /api/rules` (default: skip=0, limit=50)
2. Return a paginated response: `{"items": [...], "total": N, "skip": 0, "limit": 50}`
3. Add `total` count query to the database layer
4. Update existing tests and add pagination-specific tests

## Key Files
- `api/routers/rules.py` — the rules router (list endpoint)
- `api/schemas/rules.py` — response schemas
- `api/models/database.py` — SQLAlchemy models
- `tests/test_api_rules.py` — existing tests

## Testing
```bash
source .venv/bin/activate && python -m pytest tests/ -v
```

## Constraints
- Do not break existing tests
- Keep backward compatible — no skip/limit params = return first 50 (same as current behavior for small datasets)

## Comments

