# Test Report

## Summary
**43 tests passed, 0 failed** (39 deprecation warnings — non-blocking)

## Test Coverage

### Rule Engine (6 tests)
- ✅ Load rules from YAML
- ✅ Evaluate completeness rule (pass)
- ✅ Evaluate rule that fails threshold
- ✅ Handle unknown dimension
- ✅ Batch run multiple checks
- ✅ Test all comparison operators (gte, lte, eq)

### Dimension Calculators (14 tests)
- ✅ Completeness: full, partial, empty-as-null, empty data
- ✅ Uniqueness: all unique, duplicates, composite keys
- ✅ Accuracy: range check, pattern check, allowed values
- ✅ Consistency: date ordering, empty data
- ✅ Timeliness: fresh data, stale data
- ✅ Validity: email format, type validation, allowed values

### Rules API (7 tests)
- ✅ Create rule
- ✅ List rules with pagination
- ✅ Get rule by ID
- ✅ Get non-existent rule (404)
- ✅ Update rule
- ✅ Delete rule (soft delete)
- ✅ Filter by dimension

### Sources API (6 tests)
- ✅ Create source
- ✅ List sources
- ✅ Get source by ID
- ✅ Update source
- ✅ Delete source
- ✅ Test connection endpoint

### Connectors (4 tests)
- ✅ ADLS Gen2 implements DataConnector
- ✅ SQL Server implements DataConnector
- ✅ ADLS not connected returns False
- ✅ SQL not connected returns False

### Additional (6 tests from rule engine)
- Various operator and edge case coverage

## Warnings
- `datetime.utcnow()` deprecation (39 instances) — cosmetic, will migrate to `datetime.now(UTC)`
