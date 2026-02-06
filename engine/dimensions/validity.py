"""Validity dimension calculator.

Validates data against schema constraints, types, and format rules.
"""

import re
from typing import Any, Optional

BUILTIN_FORMATS = {
    "email": r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$",
    "phone": r"^\+?[1-9]\d{6,14}$",
    "url": r"^https?://[^\s]+$",
    "uuid": r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    "date_iso": r"^\d{4}-\d{2}-\d{2}$",
}


class ValidityCalculator:
    """Calculate data validity against schema/format rules."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate validity score for a column.

        Config options:
            expected_type: Python type name (str, int, float, bool).
            format: Built-in format name or custom regex.
            allowed_values: List of valid values.
            not_null: Whether nulls are invalid (default: False).

        Returns:
            Validity percentage (0-100).
        """
        if not data or not column:
            return 0.0

        cfg = config or {}
        expected_type = cfg.get("expected_type")
        fmt = cfg.get("format")
        allowed = cfg.get("allowed_values")
        not_null = cfg.get("not_null", False)

        pattern = None
        if fmt:
            regex = BUILTIN_FORMATS.get(fmt, fmt)
            pattern = re.compile(regex)

        type_map = {"str": str, "int": int, "float": (int, float), "bool": bool}

        total = len(data)
        valid = 0

        for row in data:
            value = row.get(column)

            if value is None:
                if not not_null:
                    valid += 1
                continue

            is_valid = True

            if expected_type and expected_type in type_map:
                if not isinstance(value, type_map[expected_type]):
                    is_valid = False

            if pattern and is_valid:
                if not pattern.match(str(value)):
                    is_valid = False

            if allowed is not None and is_valid:
                if value not in allowed:
                    is_valid = False

            if is_valid:
                valid += 1

        return (valid / total) * 100.0 if total > 0 else 0.0
