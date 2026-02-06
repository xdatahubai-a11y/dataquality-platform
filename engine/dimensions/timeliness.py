"""Timeliness/freshness dimension calculator.

Checks how recent the data is relative to a freshness threshold.
"""

from datetime import datetime, timedelta
from typing import Any, Optional


class TimelinessCalculator:
    """Calculate data timeliness (freshness)."""

    def calculate(self, data: list[dict], column: Optional[str] = None, config: Optional[dict] = None) -> float:
        """Calculate timeliness score for a timestamp column.

        Config options:
            max_age_hours: Maximum allowed age in hours (default: 24).
            reference_time: ISO timestamp to compare against (default: now).

        Returns:
            Timeliness percentage (0-100). 100 = all records within freshness SLA.
        """
        if not data or not column:
            return 0.0

        cfg = config or {}
        max_age_hours = cfg.get("max_age_hours", 24)
        ref_time_str = cfg.get("reference_time")
        ref_time = datetime.fromisoformat(ref_time_str) if ref_time_str else datetime.utcnow()
        threshold = timedelta(hours=max_age_hours)

        total = len(data)
        timely = 0

        for row in data:
            value = row.get(column)
            if value is None:
                continue
            try:
                if isinstance(value, str):
                    ts = datetime.fromisoformat(value)
                elif isinstance(value, datetime):
                    ts = value
                else:
                    continue
                if (ref_time - ts) <= threshold:
                    timely += 1
            except (ValueError, TypeError):
                pass

        return (timely / total) * 100.0 if total > 0 else 0.0
