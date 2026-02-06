"""CRUD endpoints for data sources."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.database import DataSource, gen_uuid
from api.schemas.sources import SourceCreate, SourceListResponse, SourceResponse, SourceUpdate

router = APIRouter(prefix="/api/sources", tags=["sources"])


@router.post("", response_model=SourceResponse, status_code=201)
def create_source(source: SourceCreate, db: Session = Depends(get_db)) -> DataSource:
    """Create a new data source connection."""
    db_source = DataSource(
        id=gen_uuid(),
        name=source.name,
        type=source.type,
        connection_config=json.dumps(source.connection_config),
    )
    db.add(db_source)
    db.commit()
    db.refresh(db_source)
    return db_source


@router.get("", response_model=SourceListResponse)
def list_sources(
    type: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
) -> dict:
    """List data sources with optional filtering."""
    query = db.query(DataSource)
    if type:
        query = query.filter(DataSource.type == type)
    if is_active is not None:
        query = query.filter(DataSource.is_active == is_active)
    items = query.all()
    return {"items": items, "total": len(items)}


@router.get("/{source_id}", response_model=SourceResponse)
def get_source(source_id: str, db: Session = Depends(get_db)) -> DataSource:
    """Get a data source by ID."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    return source


@router.put("/{source_id}", response_model=SourceResponse)
def update_source(source_id: str, update: SourceUpdate, db: Session = Depends(get_db)) -> DataSource:
    """Update an existing data source."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    update_data = update.model_dump(exclude_unset=True)
    if "connection_config" in update_data and update_data["connection_config"] is not None:
        update_data["connection_config"] = json.dumps(update_data["connection_config"])
    for field, value in update_data.items():
        setattr(source, field, value)
    db.commit()
    db.refresh(source)
    return source


@router.delete("/{source_id}", status_code=204)
def delete_source(source_id: str, db: Session = Depends(get_db)) -> None:
    """Soft-delete a data source."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    source.is_active = False
    db.commit()


@router.post("/{source_id}/test")
def test_connection(source_id: str, db: Session = Depends(get_db)) -> dict:
    """Test a data source connection."""
    source = db.query(DataSource).filter(DataSource.id == source_id).first()
    if not source:
        raise HTTPException(status_code=404, detail="Data source not found")
    # TODO: Implement actual connection testing via connectors
    return {"status": "ok", "message": f"Connection test for {source.name} not yet implemented"}
