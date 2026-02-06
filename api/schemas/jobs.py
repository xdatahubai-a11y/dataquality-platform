"""Pydantic schemas for DQ jobs."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class JobCreate(BaseModel):
    """Schema for submitting a DQ job."""

    source_id: str
    rule_ids: Optional[list[str]] = None  # None = all active rules for source
    parameters: Optional[dict] = None


class JobResponse(BaseModel):
    """Schema for job response."""

    id: str
    source_id: Optional[str] = None
    status: str
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    total_rules: int = 0
    passed_rules: int = 0
    failed_rules: int = 0
    error_message: Optional[str] = None

    model_config = {"from_attributes": True}


class JobListResponse(BaseModel):
    """Paginated job list response."""

    items: list[JobResponse]
    total: int
