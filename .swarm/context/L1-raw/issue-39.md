# Issue #39: fix: replace deprecated datetime.utcnow() with timezone-aware UTC

**Ingested**: 2026-03-02T16:18:06Z
**Created**: 2026-03-02T06:50:54Z
**Labels**: priority:high, agent:claude, type:bugfix, complexity:small, status:ready-for-human, attempt:2

## Body
## Problem
`datetime.utcnow()` is deprecated in Python 3.12+ (PEP 587) and will be removed in 3.14.
The codebase uses it in 10 places across 4 files, causing DeprecationWarnings.

## Files affected
- `api/models/database.py` (6 occurrences) — SQLAlchemy Column defaults
- `engine/dimensions/timeliness.py` (1 occurrence)
- `spark/dq_job.py` (1 occurrence)
- `tests/test_dimensions.py` (1 occurrence)

## Fix
Replace `datetime.utcnow()` with `datetime.now(datetime.UTC)` (or `datetime.now(timezone.utc)`).

For SQLAlchemy Column defaults, use `func.now()` from sqlalchemy or a lambda:
```python
from datetime import datetime, timezone
# Before: default=datetime.utcnow
# After:  default=lambda: datetime.now(timezone.utc)
```

## Verification
Run: `source .venv/bin/activate && python -m pytest tests/test_dimensions.py tests/test_rule_engine.py tests/test_api_rules.py -v`
All 30 tests must pass with zero DeprecationWarnings about utcnow.

## Comments

