# Merged — feat-rule-validation

**Extracted**: 2026-03-02T16:17:37Z
**Issue**: #45
**PR**: #48 — feat: add rule validation
**Agent**: claude (claude-sonnet-4-20250514)
**Type**: feature
**Attempt**: 1 (one-shot: yes)
**Total Time**: 4m

## Prompt Used
```markdown
## Task
Add validation to the rules API — reject invalid dimensions, operators, and thresholds with clear 422 errors.

## Context
Python FastAPI project. Rules have `dimension`, `operator`, `threshold` fields. Currently no validation — anything is accepted.

## Key Files (read all before coding)
- `api/schemas/rules.py` — add Pydantic validators here
- `api/routers/rules.py` — POST and PUT endpoints
- `engine/rule_engine.py` — valid dimensions: completeness, uniqueness, accuracy, consistency, timeliness, validity. Valid operators: gte, lte, gt, lt, eq.
- `tests/test_api_rules.py` — add validation tests

## Requirements
1. **Dimension validation**: must be one of: completeness, uniqueness, accuracy, consistency, timeliness, validity
2. **Operator validation**: if provided, must be one of: gte, lte, gt, lt, eq
3. **Threshold validation**: for percentage-based dimensions (completeness, uniqueness, validity), threshold must be 0-100. For other dimensions (accuracy, consistency, timeliness), no limit.
4. All validations should return HTTP 422 with clear error messages
5. Apply on both create (POST) and update (PUT) endpoints

## Implementation
Use Pydantic `field_validator` or `model_validator` in `api/schemas/rules.py`. FastAPI handles 422 responses automatically from Pydantic validation errors.

## Testing
Add these tests to `tests/test_api_rules.py`:
- Create with `dimension: "banana"` → 422
- Create with `operator: "yolo"` → 422
- Create completeness rule with `threshold: 150` → 422
- Create accuracy rule with `threshold: 150` → 201 (allowed, not percentage-based)
- Existing tests must still pass

```bash
source .venv/bin/activate && python -m pytest tests/test_api_rules.py -v
```

## Git Operations (YOU must do all of these)
1. Read key files
2. Implement validators
3. Write tests
4. Run ALL existing tests + new tests
5. `git add -A && git commit -m "feat: add rule validation — reject invalid dimensions, operators, thresholds"`
6. `git push origin feat/rule-validation`
7. `gh pr create --title "feat: add rule validation" --body "Closes #45" --base main --head feat/rule-validation --repo xdatahubai-a11y/dataquality-platform`

Do NOT stop until the PR is created.
```

## Files Changed
api/routers/rules.py
api/schemas/rules.py
tests/test_api_rules.py

## PR Description
## Summary
• Add validation to rules API to reject invalid dimensions, operators, and thresholds with clear 422 errors
• Implement Pydantic field validators for operator validation (gte, lte, gt, lt, eq)
• Add threshold range validation for percentage-based dimensions (completeness, uniqueness, validity: 0-100)
• Allow unlimited thresholds for non-percentage dimensions (accuracy, consistency, timeliness)

## Test plan
- [x] Invalid dimension "banana" → 422 error
- [x] Invalid operator "yolo" → 422 error  
- [x] Completeness rule with threshold 150 → 422 error
- [x] Accuracy rule with threshold 150 → 201 (allowed)
- [x] All existing tests still pass
- [x] Update endpoint properly validates against existing dimension

🤖 Generated with [Claude Code](https://claude.com/claude-code)

## AI Review Findings
(no AI reviews found)

## Tags
- type:feature
- agent:claude
- one-shot:yes
- issue:45
