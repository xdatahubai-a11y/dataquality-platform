"""Uniqueness dimension calculator.

Measures the percentage of unique (non-duplicate) values in a column.
"""

from typing import Any, Optional


class UniquenessCalculator:
    """Calculate data uniqueness (distinct ratio)."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate uniqueness score for a column.

        Args:
            data: List of row dicts.
            column: Column name to check.
            config: Optional config (e.g., composite_keys for multi-column uniqueness).

        Returns:
            Uniqueness percentage (0-100).
        """
        if not data:
            return 0.0

        columns = (config or {}).get("composite_keys", [column] if column else [])
        if not columns:
            return 0.0

        total = len(data)
        seen: set[tuple] = set()
        for row in data:
            key = tuple(row.get(c) for c in columns)
            seen.add(key)

        return (len(seen) / total) * 100.0 if total > 0 else 0.0
