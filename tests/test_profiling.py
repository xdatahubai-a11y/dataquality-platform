"""Tests for the profiling dimension calculator."""

from engine.dimensions.profiling import ProfilingCalculator


class TestProfiling:
    def test_numeric_column_profile(self, sample_data):
        calc = ProfilingCalculator()
        score = calc.calculate(sample_data, "age")
        details = calc._last_details

        assert details["row_count"] == 5
        assert details["null_count"] == 0
        assert details["null_percentage"] == 0.0
        assert details["distinct_count"] == 5
        assert details["distinct_percentage"] == 100.0
        assert details["min_value"] == -5
        assert details["max_value"] == 200
        assert details["mean_value"] == 59.0
        assert details["most_common"] is not None
        assert len(details["value_distribution"]) == 5
        assert score == 100.0

    def test_string_column_profile(self, sample_data):
        calc = ProfilingCalculator()
        score = calc.calculate(sample_data, "name")
        details = calc._last_details

        assert details["row_count"] == 5
        assert details["null_count"] == 1
        assert details["distinct_count"] == 4
        assert details["min_value"] is None  # non-numeric
        assert details["max_value"] is None
        assert details["mean_value"] is None
        assert score == 100.0

    def test_high_null_percentage_reduces_score(self):
        data = [{"col": None}] * 6 + [{"col": "a"}, {"col": "b"}, {"col": "c"}, {"col": "d"}]
        calc = ProfilingCalculator()
        score = calc.calculate(data, "col")
        assert score == 80.0  # -20 for >50% nulls

    def test_low_cardinality_reduces_score(self):
        # 100 rows, only 5 distinct values -> 5% distinct
        data = [{"col": i % 5} for i in range(100)]
        calc = ProfilingCalculator()
        score = calc.calculate(data, "col")
        assert score == 85.0  # -15 for <10% distinct

    def test_all_same_values_reduces_score(self):
        data = [{"col": "same"}] * 10
        calc = ProfilingCalculator()
        score = calc.calculate(data, "col")
        # distinct_percentage = 10% (1/10=10%), so <10% doesn't trigger
        # but all same: -15
        assert score == 85.0

    def test_empty_data_returns_zero(self):
        calc = ProfilingCalculator()
        assert calc.calculate([], "col") == 0.0

    def test_mixed_types_detection(self):
        data = [{"col": 1}, {"col": "two"}, {"col": 3}]
        calc = ProfilingCalculator()
        score = calc.calculate(data, "col")
        details = calc._last_details

        assert details["has_mixed_types"] is True
        assert score == 90.0  # -10 for mixed types

    def test_value_distribution_returns_top_5(self):
        data = [{"col": v} for v in ["a"] * 10 + ["b"] * 8 + ["c"] * 6 + ["d"] * 4 + ["e"] * 2 + ["f"] * 1]
        calc = ProfilingCalculator()
        calc.calculate(data, "col")
        details = calc._last_details

        dist = details["value_distribution"]
        assert len(dist) == 5
        assert dist[0]["value"] == "a"
        assert dist[0]["count"] == 10
        assert dist[4]["value"] == "e"
        assert dist[4]["count"] == 2
