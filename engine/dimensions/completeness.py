"""Completeness dimension calculator.

Measures the percentage of non-null/non-empty values in a column.
"""

from typing import Any, Optional


class CompletenessCalculator:
    """Calculate data completeness (non-null ratio)."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate completeness score for a column.

        Args:
            data: List of row dicts.
            column: Column name to check.
            config: Optional config (e.g., treat_empty_as_null: true).

        Returns:
            Completeness percentage (0-100).
        """
        if not data or not column:
            return 0.0

        treat_empty = (config or {}).get("treat_empty_as_null", True)
        total = len(data)
        non_null = 0

        for row in data:
            value = row.get(column)
            if value is None:
                continue
            if treat_empty and isinstance(value, str) and value.strip() == "":
                continue
            non_null += 1

        return (non_null / total) * 100.0 if total > 0 else 0.0
