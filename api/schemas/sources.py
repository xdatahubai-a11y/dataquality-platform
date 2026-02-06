"""Pydantic schemas for data sources."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator


class SourceCreate(BaseModel):
    """Schema for creating a data source."""

    name: str = Field(..., min_length=1, max_length=255)
    type: str = Field(..., pattern="^(adls_gen2|delta_table|sql_server)$")
    connection_config: dict


class SourceUpdate(BaseModel):
    """Schema for updating a data source."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    type: Optional[str] = Field(None, pattern="^(adls_gen2|delta_table|sql_server)$")
    connection_config: Optional[dict] = None
    is_active: Optional[bool] = None


class SourceResponse(BaseModel):
    """Schema for data source response."""

    id: str
    name: str
    type: str
    connection_config: dict
    is_active: bool
    last_tested_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}

    @field_validator("connection_config", mode="before")
    @classmethod
    def parse_connection_config(cls, v: str | dict) -> dict:
        if isinstance(v, str):
            import json
            return json.loads(v)
        return v


class SourceListResponse(BaseModel):
    """Paginated source list response."""

    items: list[SourceResponse]
    total: int
