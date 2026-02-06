"""Consistency dimension calculator.

Checks cross-column relationships and referential integrity.
"""

from typing import Any, Optional


class ConsistencyCalculator:
    """Calculate data consistency (cross-column rules)."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate consistency score.

        Config options:
            rule: Expression like "start_date < end_date".
            column_a: First column name.
            column_b: Second column name.
            operator: Comparison operator (lt, lte, gt, gte, eq, neq).

        Returns:
            Consistency percentage (0-100).
        """
        if not data:
            return 0.0

        cfg = config or {}
        col_a = cfg.get("column_a", column)
        col_b = cfg.get("column_b")
        operator = cfg.get("operator", "lt")

        if not col_a or not col_b:
            return 0.0

        total = len(data)
        consistent = 0

        for row in data:
            val_a = row.get(col_a)
            val_b = row.get(col_b)
            if val_a is None or val_b is None:
                continue
            try:
                if operator == "lt" and val_a < val_b:
                    consistent += 1
                elif operator == "lte" and val_a <= val_b:
                    consistent += 1
                elif operator == "gt" and val_a > val_b:
                    consistent += 1
                elif operator == "gte" and val_a >= val_b:
                    consistent += 1
                elif operator == "eq" and val_a == val_b:
                    consistent += 1
                elif operator == "neq" and val_a != val_b:
                    consistent += 1
            except TypeError:
                pass

        return (consistent / total) * 100.0 if total > 0 else 0.0
