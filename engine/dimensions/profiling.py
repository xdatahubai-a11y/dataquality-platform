"""Profiling dimension calculator.

Computes column statistics and returns a data quality readiness score.
"""

from collections import Counter
from typing import Any, Optional


class ProfilingCalculator:
    """Calculate data profiling statistics and readiness score."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate profiling score for a column.

        Computes comprehensive column statistics (row count, nulls, distinct
        values, min/max/mean, most common value, value distribution) and
        returns a quality readiness score (0-100).

        Args:
            data: List of row dicts.
            column: Column name to profile.
            config: Optional config dict.

        Returns:
            Profiling readiness score (0-100).
        """
        if not data or not column:
            return 0.0

        row_count = len(data)
        values = [row.get(column) for row in data]
        null_count = sum(1 for v in values if v is None)
        non_null_values = [v for v in values if v is not None]
        non_null_count = len(non_null_values)
        null_percentage = (null_count / row_count) * 100.0 if row_count > 0 else 0.0

        distinct_count = len(set(non_null_values))
        distinct_percentage = (distinct_count / non_null_count) * 100.0 if non_null_count > 0 else 0.0

        # Numeric stats
        numeric_values = [v for v in non_null_values if isinstance(v, (int, float))]
        min_value = min(numeric_values) if numeric_values else None
        max_value = max(numeric_values) if numeric_values else None
        mean_value = sum(numeric_values) / len(numeric_values) if numeric_values else None

        # Most common value
        counter = Counter(non_null_values)
        most_common_entry = counter.most_common(1)
        most_common = {"value": most_common_entry[0][0], "count": most_common_entry[0][1]} if most_common_entry else None

        # Value distribution (top 5)
        value_distribution = [{"value": v, "count": c} for v, c in counter.most_common(5)]

        # Mixed types detection
        types_present = set(type(v).__name__ for v in non_null_values)
        has_mixed_types = len(types_present) > 1

        # Store details
        self._last_details = {
            "row_count": row_count,
            "null_count": null_count,
            "null_percentage": round(null_percentage, 2),
            "distinct_count": distinct_count,
            "distinct_percentage": round(distinct_percentage, 2),
            "min_value": min_value,
            "max_value": max_value,
            "mean_value": round(mean_value, 2) if mean_value is not None else None,
            "most_common": most_common,
            "value_distribution": value_distribution,
            "has_mixed_types": has_mixed_types,
        }

        # Scoring
        score = 100.0

        if null_percentage > 50.0:
            score -= 20.0

        if non_null_count > 0 and distinct_percentage < 10.0:
            score -= 15.0

        if distinct_count <= 1 and non_null_count > 0:
            score -= 15.0

        if has_mixed_types:
            score -= 10.0

        return max(score, 0.0)
