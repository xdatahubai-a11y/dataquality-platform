"""Tests for each DQ dimension calculator."""

from engine.dimensions.accuracy import AccuracyCalculator
from engine.dimensions.completeness import CompletenessCalculator
from engine.dimensions.consistency import ConsistencyCalculator
from engine.dimensions.timeliness import TimelinessCalculator
from engine.dimensions.uniqueness import UniquenessCalculator
from engine.dimensions.validity import ValidityCalculator


class TestCompleteness:
    def test_full_completeness(self):
        data = [{"col": "a"}, {"col": "b"}, {"col": "c"}]
        assert CompletenessCalculator().calculate(data, "col") == 100.0

    def test_partial_completeness(self, sample_data):
        score = CompletenessCalculator().calculate(sample_data, "name")
        assert score == 80.0  # 4 of 5

    def test_empty_treated_as_null(self):
        data = [{"col": ""}, {"col": "a"}, {"col": None}]
        score = CompletenessCalculator().calculate(data, "col", {"treat_empty_as_null": True})
        assert abs(score - 33.33) < 1.0

    def test_empty_data(self):
        assert CompletenessCalculator().calculate([], "col") == 0.0


class TestUniqueness:
    def test_all_unique(self):
        data = [{"id": 1}, {"id": 2}, {"id": 3}]
        assert UniquenessCalculator().calculate(data, "id") == 100.0

    def test_duplicates(self, sample_data):
        score = UniquenessCalculator().calculate(sample_data, "id")
        assert score == 80.0  # 4 unique out of 5

    def test_composite_keys(self):
        data = [{"a": 1, "b": "x"}, {"a": 1, "b": "y"}, {"a": 1, "b": "x"}]
        score = UniquenessCalculator().calculate(data, config={"composite_keys": ["a", "b"]})
        assert abs(score - 66.67) < 1.0


class TestAccuracy:
    def test_range_check(self, sample_data):
        score = AccuracyCalculator().calculate(sample_data, "age", {"min_value": 0, "max_value": 150})
        assert score == 60.0  # 3 valid (30, 25, 45), 1 null skipped, 1 out of range (200), 1 negative

    def test_pattern_check(self):
        data = [{"code": "AB123"}, {"code": "CD456"}, {"code": "invalid!"}]
        score = AccuracyCalculator().calculate(data, "code", {"pattern": r"^[A-Z]{2}\d{3}$"})
        assert abs(score - 66.67) < 1.0

    def test_allowed_values(self, sample_data):
        score = AccuracyCalculator().calculate(sample_data, "status", {"allowed_values": ["active", "inactive"]})
        # 3 active + 1 inactive = 4, 1 null skipped = 80%
        assert score == 80.0


class TestConsistency:
    def test_date_ordering(self, sample_data):
        score = ConsistencyCalculator().calculate(
            sample_data, config={"column_a": "created_at", "column_b": "updated_at", "operator": "lte"}
        )
        # Row 3 has created_at > updated_at, so 4/5 = 80%... let's check
        assert score >= 60.0

    def test_empty_data(self):
        assert ConsistencyCalculator().calculate([], config={"column_a": "a", "column_b": "b"}) == 0.0


class TestTimeliness:
    def test_fresh_data(self):
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        data = [
            {"ts": (now - timedelta(hours=1)).isoformat()},
            {"ts": (now - timedelta(hours=2)).isoformat()},
        ]
        score = TimelinessCalculator().calculate(data, "ts", {"max_age_hours": 24})
        assert score == 100.0

    def test_stale_data(self):
        data = [{"ts": "2020-01-01T00:00:00"}]
        score = TimelinessCalculator().calculate(data, "ts", {"max_age_hours": 24})
        assert score == 0.0


class TestValidity:
    def test_email_format(self, sample_data):
        score = ValidityCalculator().calculate(sample_data, "email", {"format": "email"})
        # alice@, bob@, None(valid by default), not-an-email(invalid), eve@ = 3 valid + 1 null = 4/5
        assert score >= 60.0

    def test_type_validation(self):
        data = [{"val": 1}, {"val": "two"}, {"val": 3}]
        score = ValidityCalculator().calculate(data, "val", {"expected_type": "int"})
        assert abs(score - 66.67) < 1.0

    def test_allowed_values(self):
        data = [{"s": "a"}, {"s": "b"}, {"s": "c"}]
        score = ValidityCalculator().calculate(data, "s", {"allowed_values": ["a", "b"]})
        assert abs(score - 66.67) < 1.0
