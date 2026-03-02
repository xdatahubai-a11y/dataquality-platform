"""Pydantic schemas for DQ rules."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator, ValidationInfo


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

    @field_validator('operator')
    @classmethod
    def validate_operator(cls, v: Optional[str]) -> Optional[str]:
        """Validate operator is one of allowed values."""
        if v is None:
            return v
        valid_operators = {'gte', 'lte', 'gt', 'lt', 'eq'}
        if v not in valid_operators:
            raise ValueError(f'operator must be one of: {", ".join(sorted(valid_operators))}')
        return v

    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        """Validate threshold range based on dimension type."""
        if v is None:
            return v

        # Get dimension from values dict (it's validated before threshold)
        dimension = info.data.get('dimension') if info.data else None
        if dimension in {'completeness', 'uniqueness', 'validity'}:
            if not (0 <= v <= 100):
                raise ValueError(f'threshold for {dimension} dimension must be between 0 and 100')

        return v


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

    @field_validator('operator')
    @classmethod
    def validate_operator(cls, v: Optional[str]) -> Optional[str]:
        """Validate operator is one of allowed values."""
        if v is None:
            return v
        valid_operators = {'gte', 'lte', 'gt', 'lt', 'eq'}
        if v not in valid_operators:
            raise ValueError(f'operator must be one of: {", ".join(sorted(valid_operators))}')
        return v

    @field_validator('threshold')
    @classmethod
    def validate_threshold(cls, v: Optional[float], info: ValidationInfo) -> Optional[float]:
        """Validate threshold range based on dimension type."""
        if v is None:
            return v

        # Get dimension from values dict (it's validated before threshold)
        dimension = info.data.get('dimension') if info.data else None
        if dimension in {'completeness', 'uniqueness', 'validity'}:
            if not (0 <= v <= 100):
                raise ValueError(f'threshold for {dimension} dimension must be between 0 and 100')

        return v


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
