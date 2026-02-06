"""Pydantic schemas for DQ rules."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class RuleCreate(BaseModel):
    """Schema for creating a new rule."""

    name: str = Field(..., min_length=1, max_length=255)
    description: Optional[str] = None
    dimension: str = Field(..., pattern="^(completeness|uniqueness|accuracy|consistency|timeliness|validity)$")
    source_id: Optional[str] = None
    column_name: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    config: Optional[dict] = None
    severity: str = Field(default="warning", pattern="^(info|warning|critical)$")


class RuleUpdate(BaseModel):
    """Schema for updating a rule."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    dimension: Optional[str] = Field(None, pattern="^(completeness|uniqueness|accuracy|consistency|timeliness|validity)$")
    column_name: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    config: Optional[dict] = None
    severity: Optional[str] = Field(None, pattern="^(info|warning|critical)$")
    is_active: Optional[bool] = None


class RuleResponse(BaseModel):
    """Schema for rule response."""

    id: str
    name: str
    description: Optional[str] = None
    dimension: str
    source_id: Optional[str] = None
    column_name: Optional[str] = None
    operator: Optional[str] = None
    threshold: Optional[float] = None
    config: Optional[dict] = None
    severity: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class RuleListResponse(BaseModel):
    """Paginated rule list response."""

    items: list[RuleResponse]
    total: int
    page: int
    page_size: int
