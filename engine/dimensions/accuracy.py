"""Accuracy dimension calculator.

Validates data accuracy via regex patterns, value ranges, or reference lookups.
"""

import re
from typing import Any, Optional


class AccuracyCalculator:
    """Calculate data accuracy against expected patterns or ranges."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate accuracy score for a column.

        Config options:
            pattern: Regex pattern that values must match.
            min_value: Minimum allowed numeric value.
            max_value: Maximum allowed numeric value.
            allowed_values: List of valid values.

        Returns:
            Accuracy percentage (0-100).
        """
        if not data or not column:
            return 0.0

        cfg = config or {}
        total = len(data)
        accurate = 0

        pattern = cfg.get("pattern")
        compiled = re.compile(pattern) if pattern else None
        min_val = cfg.get("min_value")
        max_val = cfg.get("max_value")
        allowed = set(cfg.get("allowed_values", []))

        for row in data:
            value = row.get(column)
            if value is None:
                continue

            if compiled:
                if compiled.match(str(value)):
                    accurate += 1
            elif allowed:
                if value in allowed:
                    accurate += 1
            elif min_val is not None or max_val is not None:
                try:
                    num = float(value)
                    in_range = True
                    if min_val is not None and num < min_val:
                        in_range = False
                    if max_val is not None and num > max_val:
                        in_range = False
                    if in_range:
                        accurate += 1
                except (ValueError, TypeError):
                    pass
            else:
                accurate += 1  # No validation config = assume accurate

        return (accurate / total) * 100.0 if total > 0 else 0.0
