"""Endpoints for DQ job submission and monitoring."""

import json
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.database import DQRun, DQResult, Rule, DataSource, gen_uuid
from api.schemas.jobs import JobCreate, JobListResponse, JobResponse
from engine.rule_engine import RuleDefinition, run_checks
from connectors import get_connector

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=201)
def submit_job(job: JobCreate, db: Session = Depends(get_db)) -> DQRun:
    """Submit a new DQ check job."""
    db_run = DQRun(
        id=gen_uuid(),
        source_id=job.source_id,
        status="running",
        started_at=datetime.now(timezone.utc),
        parameters=json.dumps({
            "rule_ids": job.rule_ids,
            **(job.parameters or {}),
        }),
    )
    db.add(db_run)
    db.commit()
    db.refresh(db_run)

    try:
        # Execute the DQ checks locally
        _execute_dq_checks(db_run, db)
        db.commit()
    except Exception as e:
        # Update status to failed on any error
        db_run.status = "failed"
        db_run.error_message = str(e)
        db_run.completed_at = datetime.now(timezone.utc)
        db.commit()
        db.refresh(db_run)

    return db_run


def _execute_dq_checks(db_run: DQRun, db: Session) -> None:
    """Execute DQ checks for a run and store results."""
    # 1. Load the data source
    source = db.query(DataSource).filter(DataSource.id == db_run.source_id).first()
    if not source:
        raise ValueError(f"Data source not found: {db_run.source_id}")

    # Parse source configuration
    source_config = json.loads(source.connection_config)

    # 2. Load rules from database
    params = json.loads(db_run.parameters or "{}")
    rule_ids = params.get("rule_ids")

    if rule_ids:
        # Use specified rule IDs
        db_rules = db.query(Rule).filter(Rule.id.in_(rule_ids), Rule.is_active == True).all()
    else:
        # Use all active rules for the source
        db_rules = db.query(Rule).filter(Rule.source_id == db_run.source_id, Rule.is_active == True).all()

    if not db_rules:
        raise ValueError("No active rules found for execution")

    # Convert database rules to RuleDefinition objects
    rules = []
    for db_rule in db_rules:
        rule_config = json.loads(db_rule.config or "{}")
        rules.append(RuleDefinition(
            name=db_rule.name,
            dimension=db_rule.dimension,
            column=db_rule.column_name,
            operator=db_rule.operator or "gte",
            threshold=db_rule.threshold,
            config=rule_config,
            severity=db_rule.severity
        ))

    # 3. Get connector and connect to data source
    connector_class = get_connector(source.type)
    connector = connector_class()
    connector.connect(source_config)

    # 4. Read data from the source
    # For simplicity, use the first table if no specific path is configured
    tables = connector.list_tables()
    if not tables:
        raise ValueError("No tables found in data source")

    # Use the first table or a configured table path
    table_name = params.get("table_name", tables[0])
    limit = params.get("limit", 10000)  # Default limit to avoid memory issues

    data = connector.read_data(table_name, limit=limit)
    connector.close()

    if not data:
        raise ValueError("No data found in source")

    # 5. Run DQ checks
    check_results = run_checks(rules, data)

    # 6. Store results in database
    passed_count = 0
    failed_count = 0

    for result in check_results:
        # Find the corresponding rule to get its ID
        db_rule = next((r for r in db_rules if r.name == result.rule_name), None)
        if not db_rule:
            continue

        db_result = DQResult(
            id=gen_uuid(),
            run_id=db_run.id,
            rule_id=db_rule.id,
            dimension=result.dimension,
            column_name=result.column,
            metric_value=result.metric_value,
            threshold=result.threshold,
            passed=result.passed,
            details=json.dumps(result.details)
        )
        db.add(db_result)

        if result.passed:
            passed_count += 1
        else:
            failed_count += 1

    # 7. Update run status and statistics
    db_run.status = "completed"
    db_run.completed_at = datetime.now(timezone.utc)
    db_run.total_rules = len(check_results)
    db_run.passed_rules = passed_count
    db_run.failed_rules = failed_count


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
