# Issue #45: feat: add rule validation on create/update — reject invalid dimensions, operators, thresholds

**Ingested**: 2026-03-02T16:18:01Z
**Created**: 2026-03-02T07:42:53Z
**Labels**: agent:claude, type:feature, status:ready-for-human, complexity:medium, attempt:1, priority:medium

## Body
## Problem
The rules API accepts any values for dimension, operator, threshold — including nonsense like `dimension: 'banana'` or `operator: 'yolo'`. No validation.

## Requirements
1. Validate `dimension` is one of: completeness, uniqueness, accuracy, consistency, timeliness, validity
2. Validate `operator` is one of: gte, lte, gt, lt, eq (if provided)
3. Validate `threshold` is between 0 and 100 for percentage-based dimensions (completeness, uniqueness, validity)
4. Return 422 with clear error messages for invalid values
5. Apply validation on both POST (create) and PUT (update) endpoints

## Key Files
- `api/schemas/rules.py` — add Pydantic validators here
- `api/routers/rules.py` — may need error handling
- `engine/rule_engine.py` — reference for valid dimensions/operators
- `tests/test_api_rules.py` — add validation tests

## Testing
Add to `tests/test_api_rules.py`:
- Create rule with invalid dimension → 422
- Create rule with invalid operator → 422  
- Create rule with threshold > 100 for completeness → 422
- Create rule with valid threshold for accuracy (no % limit) → 201

Run: `source .venv/bin/activate && python -m pytest tests/test_api_rules.py -v`

## Constraints
- Use Pydantic validators (field_validator or model_validator)
- Don't break existing tests — existing valid rules must still work
- Keep error messages user-friendly

## Comments

