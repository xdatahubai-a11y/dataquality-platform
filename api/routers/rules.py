"""CRUD endpoints for DQ rules."""

import json
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.dependencies import get_db
from api.models.database import Rule, gen_uuid
from api.schemas.rules import RuleCreate, RuleListResponse, RuleResponse, RuleUpdate

router = APIRouter(prefix="/api/rules", tags=["rules"])


@router.post("", response_model=RuleResponse, status_code=201)
def create_rule(rule: RuleCreate, db: Session = Depends(get_db)) -> Rule:
    """Create a new DQ rule."""
    db_rule = Rule(
        id=gen_uuid(),
        name=rule.name,
        description=rule.description,
        dimension=rule.dimension,
        source_id=rule.source_id,
        column_name=rule.column_name,
        operator=rule.operator,
        threshold=rule.threshold,
        config=json.dumps(rule.config) if rule.config else None,
        severity=rule.severity,
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


@router.get("", response_model=RuleListResponse)
def list_rules(
    dimension: Optional[str] = None,
    is_active: Optional[bool] = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> dict:
    """List rules with optional filtering."""
    query = db.query(Rule)
    if dimension:
        query = query.filter(Rule.dimension == dimension)
    if is_active is not None:
        query = query.filter(Rule.is_active == is_active)
    total = query.count()
    items = query.offset((page - 1) * page_size).limit(page_size).all()
    return {"items": items, "total": total, "page": page, "page_size": page_size}


@router.get("/{rule_id}", response_model=RuleResponse)
def get_rule(rule_id: str, db: Session = Depends(get_db)) -> Rule:
    """Get a rule by ID."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule


@router.put("/{rule_id}", response_model=RuleResponse)
def update_rule(rule_id: str, update: RuleUpdate, db: Session = Depends(get_db)) -> Rule:
    """Update an existing rule."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    update_data = update.model_dump(exclude_unset=True)
    if "config" in update_data and update_data["config"] is not None:
        update_data["config"] = json.dumps(update_data["config"])
    for field, value in update_data.items():
        setattr(rule, field, value)
    db.commit()
    db.refresh(rule)
    return rule


@router.delete("/{rule_id}", status_code=204)
def delete_rule(rule_id: str, db: Session = Depends(get_db)) -> None:
    """Soft-delete a rule by setting is_active=False."""
    rule = db.query(Rule).filter(Rule.id == rule_id).first()
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    rule.is_active = False
    db.commit()
