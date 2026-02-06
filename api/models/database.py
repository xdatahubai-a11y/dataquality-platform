"""SQLAlchemy ORM models for the DataQuality Platform."""

import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    """Base class for all models."""
    pass


def gen_uuid() -> str:
    """Generate a UUID string."""
    return str(uuid.uuid4())


class Rule(Base):
    """DQ rule definition."""

    __tablename__ = "rules"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    name: str = Column(String(255), nullable=False)
    description: str = Column(Text, nullable=True)
    dimension: str = Column(String(50), nullable=False)
    source_id: str = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    column_name: str = Column(String(255), nullable=True)
    operator: str = Column(String(50), nullable=True)
    threshold: float = Column(Float, nullable=True)
    config: str = Column(Text, nullable=True)  # JSON string for extra config
    severity: str = Column(String(20), default="warning")
    is_active: bool = Column(Boolean, default=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    source = relationship("DataSource", back_populates="rules")
    results = relationship("DQResult", back_populates="rule")


class DataSource(Base):
    """Data source connection configuration."""

    __tablename__ = "data_sources"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    name: str = Column(String(255), nullable=False)
    type: str = Column(String(50), nullable=False)  # adls_gen2, delta_table, sql_server
    connection_config: str = Column(Text, nullable=False)  # JSON string
    is_active: bool = Column(Boolean, default=True)
    last_tested_at: datetime = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
    updated_at: datetime = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    rules = relationship("Rule", back_populates="source")
    runs = relationship("DQRun", back_populates="source")
    scores = relationship("DQScore", back_populates="source")


class DQRun(Base):
    """A single DQ check execution run."""

    __tablename__ = "dq_runs"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    source_id: str = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    status: str = Column(String(20), nullable=False, default="pending")
    started_at: datetime = Column(DateTime, nullable=True)
    completed_at: datetime = Column(DateTime, nullable=True)
    total_rules: int = Column(Integer, default=0)
    passed_rules: int = Column(Integer, default=0)
    failed_rules: int = Column(Integer, default=0)
    error_message: str = Column(Text, nullable=True)
    parameters: str = Column(Text, nullable=True)  # JSON

    source = relationship("DataSource", back_populates="runs")
    results = relationship("DQResult", back_populates="run")
    scores = relationship("DQScore", back_populates="run")


class DQResult(Base):
    """Individual rule check result within a run."""

    __tablename__ = "dq_results"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    run_id: str = Column(String(36), ForeignKey("dq_runs.id"), nullable=False)
    rule_id: str = Column(String(36), ForeignKey("rules.id"), nullable=False)
    dimension: str = Column(String(50))
    column_name: str = Column(String(255), nullable=True)
    metric_value: float = Column(Float)
    threshold: float = Column(Float, nullable=True)
    passed: bool = Column(Boolean)
    details: str = Column(Text, nullable=True)  # JSON
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    run = relationship("DQRun", back_populates="results")
    rule = relationship("Rule", back_populates="results")


class DQScore(Base):
    """Aggregate DQ score per dimension per run."""

    __tablename__ = "dq_scores"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    run_id: str = Column(String(36), ForeignKey("dq_runs.id"), nullable=False)
    source_id: str = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    dimension: str = Column(String(50))
    score: float = Column(Float, nullable=False)
    total_checks: int = Column(Integer, default=0)
    passed_checks: int = Column(Integer, default=0)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)

    run = relationship("DQRun", back_populates="scores")
    source = relationship("DataSource", back_populates="scores")


class Schedule(Base):
    """Scheduled DQ check configuration."""

    __tablename__ = "schedules"

    id: str = Column(String(36), primary_key=True, default=gen_uuid)
    name: str = Column(String(255))
    source_id: str = Column(String(36), ForeignKey("data_sources.id"), nullable=True)
    cron_expression: str = Column(String(100))
    rule_ids: str = Column(Text, nullable=True)  # JSON array
    is_active: bool = Column(Boolean, default=True)
    last_run_at: datetime = Column(DateTime, nullable=True)
    next_run_at: datetime = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, default=datetime.utcnow)
