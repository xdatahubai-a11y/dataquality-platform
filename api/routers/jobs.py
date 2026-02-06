"""Endpoints for DQ job submission and monitoring."""

import json
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.database import DQRun, gen_uuid
from api.schemas.jobs import JobCreate, JobListResponse, JobResponse

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def submit_job(job: JobCreate, db: Session = Depends(get_db)) -> DQRun:
    """Submit a new DQ check job."""
    db_run = DQRun(
        id=gen_uuid(),
        source_id=job.source_id,
        status="pending",
        parameters=json.dumps({
            "rule_ids": job.rule_ids,
            **(job.parameters or {}),
        }),
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)
    # TODO: Dispatch to Spark via spark/submit.py
    return db_run


@router.get("", response_model=JobListResponse)
def list_jobs(
    status: Optional[str] = None,
    source_id: Optional[str] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """List DQ jobs with optional filtering."""
    query = db.query(DQRun)
    if status:
        query = query.filter(DQRun.status == status)
    if source_id:
        query = query.filter(DQRun.source_id == source_id)
    total = query.count()
    items = query.order_by(DQRun.started_at.desc()).offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total}


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: str, db: Session = Depends(get_db)) -> DQRun:
    """Get job status and details."""
    run = db.query(DQRun).filter(DQRun.id == job_id).first()
    if not run:
        raise HTTPException(status_code=404, detail="Job not found")
    return run


@router.post("/{job_id}/retry", response_model=JobResponse)
def retry_job(job_id: str, db: Session = Depends(get_db)) -> DQRun:
    """Retry a failed job."""
    original = db.query(DQRun).filter(DQRun.id == job_id).first()
    if not original:
        raise HTTPException(status_code=404, detail="Job not found")
    if original.status not in ("failed", "completed"):
        raise HTTPException(status_code=400, detail="Can only retry failed or completed jobs")
    new_run = DQRun(
        id=gen_uuid(),
        source_id=original.source_id,
        status="pending",
        parameters=original.parameters,
    )
    db.add(new_run)
    db.commit()
    db.refresh(new_run)
    return new_run
