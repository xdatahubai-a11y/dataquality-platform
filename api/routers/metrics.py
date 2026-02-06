"""Endpoints for DQ metrics and scores."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.database import DQRun, DQScore, DataSource
from api.schemas.metrics import DimensionScore, MetricsSummary, SourceMetrics

router = APIRouter(prefix="/api/metrics", tags=["metrics"])


@router.get("/summary", response_model=MetricsSummary)
def get_summary(db: Session = Depends(get_db)) -> dict:
    """Get overall DQ metrics summary across all sources."""
    scores = db.query(DQScore).all()
    if not scores:
        return {"overall_score": 0.0, "dimensions": [], "total_runs": 0, "last_run_at": None}

    dim_groups: dict[str, list[float]] = {}
    for s in scores:
        dim_groups.setdefault(s.dimension, []).append(s.score)

    dimensions = [
        DimensionScore(
            dimension=dim,
            score=round(sum(vals) / len(vals), 2),
            total_checks=len(vals),
            passed_checks=sum(1 for v in vals if v >= 80.0),
        )
        for dim, vals in dim_groups.items()
    ]

    overall = round(sum(d.score for d in dimensions) / len(dimensions), 2) if dimensions else 0.0
    total_runs = db.query(func.count(DQRun.id)).scalar() or 0
    last_run = db.query(func.max(DQRun.completed_at)).scalar()

    return {
        "overall_score": overall,
        "dimensions": dimensions,
        "total_runs": total_runs,
        "last_run_at": last_run,
    }


@router.get("/dimensions")
def get_dimension_scores(db: Session = Depends(get_db)) -> list[DimensionScore]:
    """Get per-dimension DQ scores."""
    scores = db.query(DQScore).all()
    dim_groups: dict[str, list[float]] = {}
    for s in scores:
        dim_groups.setdefault(s.dimension, []).append(s.score)

    return [
        DimensionScore(
            dimension=dim,
            score=round(sum(vals) / len(vals), 2),
            total_checks=len(vals),
            passed_checks=sum(1 for v in vals if v >= 80.0),
        )
        for dim, vals in dim_groups.items()
    ]


@router.get("/sources/{source_id}", response_model=SourceMetrics)
def get_source_metrics(source_id: str, db: Session = Depends(get_db)) -> dict:
    """Get DQ metrics for a specific data source."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Source not found")

    scores = db.query(DQScore).filter(DQScore.source_id == source_id).all()
    dim_groups: dict[str, list[float]] = {}
    for s in scores:
        dim_groups.setdefault(s.dimension, []).append(s.score)

    dimensions = [
        DimensionScore(
            dimension=dim,
            score=round(sum(vals) / len(vals), 2),
            total_checks=len(vals),
            passed_checks=sum(1 for v in vals if v >= 80.0),
        )
        for dim, vals in dim_groups.items()
    ]

    overall = round(sum(d.score for d in dimensions) / len(dimensions), 2) if dimensions else 0.0
    run_count = db.query(func.count(DQRun.id)).filter(DQRun.source_id == source_id).scalar() or 0
    last_run = db.query(func.max(DQRun.completed_at)).filter(DQRun.source_id == source_id).scalar()

    return {
        "source_id": source_id,
        "source_name": source.name,
        "overall_score": overall,
        "dimensions": dimensions,
        "last_run_at": last_run,
        "run_count": run_count,
    }
