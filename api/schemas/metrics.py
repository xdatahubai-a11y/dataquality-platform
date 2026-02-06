"""Pydantic schemas for DQ metrics and scores."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class DimensionScore(BaseModel):
    """Score for a single DQ dimension."""

    dimension: str
    score: float
    total_checks: int
    passed_checks: int


class MetricsSummary(BaseModel):
    """Overall DQ metrics summary."""

    overall_score: float
    dimensions: list[DimensionScore]
    total_runs: int
    last_run_at: Optional[datetime] = None


class HistoricalScore(BaseModel):
    """Historical DQ score data point."""

    date: datetime
    overall_score: float
    dimensions: list[DimensionScore]


class SourceMetrics(BaseModel):
    """DQ metrics for a specific data source."""

    source_id: str
    source_name: str
    overall_score: float
    dimensions: list[DimensionScore]
    last_run_at: Optional[datetime] = None
    run_count: int = 0
