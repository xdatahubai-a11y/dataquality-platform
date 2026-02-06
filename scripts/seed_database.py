#!/usr/bin/env python3
"""Seed the PostgreSQL metadata DB with test data sources, rules, and schedules.

Uses SQLAlchemy models from api/models/database.py.
Requires DQ_DATABASE_URL env var (defaults to local docker-compose).
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from api.models.database import Base, DataSource, Rule, Schedule

DATABASE_URL = os.environ.get(
    "DQ_DATABASE_URL", "postgresql://dq:dqpass@localhost:5432/dataquality"
)

SOURCES = [
    {"name": "customers", "type": "csv", "connection_config": json.dumps({"path": "test_data/customers.csv"})},
    {"name": "orders", "type": "csv", "connection_config": json.dumps({"path": "test_data/orders.csv"})},
    {"name": "products", "type": "csv", "connection_config": json.dumps({"path": "test_data/products.csv"})},
    {"name": "corrupted", "type": "csv", "connection_config": json.dumps({"path": "test_data/corrupted.csv"})},
]


def build_rules(source_id: str, source_name: str) -> list[dict]:
    """Build DQ rules for a given data source."""
    rules: list[dict] = []
    if source_name == "customers":
        rules = [
            {"name": "email_completeness", "dimension": "completeness", "column_name": "email", "threshold": 0.95, "severity": "critical"},
            {"name": "customer_id_uniqueness", "dimension": "uniqueness", "column_name": "customer_id", "threshold": 1.0, "severity": "critical"},
            {"name": "email_validity", "dimension": "validity", "column_name": "email", "threshold": 0.90, "config": json.dumps({"pattern": r"^[^@]+@[^@]+\.[^@]+$"})},
            {"name": "age_accuracy", "dimension": "accuracy", "column_name": "age", "threshold": 0.95, "config": json.dumps({"min": 0, "max": 150})},
            {"name": "status_validity", "dimension": "validity", "column_name": "status", "threshold": 0.95, "config": json.dumps({"allowed": ["active", "inactive", "suspended"]})},
            {"name": "date_consistency", "dimension": "consistency", "column_name": "created_at", "threshold": 0.95, "config": json.dumps({"rule": "created_at <= updated_at"})},
        ]
    elif source_name == "orders":
        rules = [
            {"name": "order_completeness", "dimension": "completeness", "column_name": "order_id", "threshold": 1.0},
            {"name": "order_id_uniqueness", "dimension": "uniqueness", "column_name": "order_id", "threshold": 1.0},
            {"name": "amount_accuracy", "dimension": "accuracy", "column_name": "amount", "threshold": 0.99, "config": json.dumps({"min": 0, "max": 10000})},
            {"name": "order_timeliness", "dimension": "timeliness", "column_name": "order_date", "threshold": 0.80, "config": json.dumps({"max_age_days": 365})},
            {"name": "status_validity", "dimension": "validity", "column_name": "status", "threshold": 1.0, "config": json.dumps({"allowed": ["completed", "pending", "shipped"]})},
        ]
    elif source_name == "products":
        rules = [
            {"name": "product_completeness", "dimension": "completeness", "column_name": "product_id", "threshold": 1.0},
            {"name": "product_id_uniqueness", "dimension": "uniqueness", "column_name": "product_id", "threshold": 1.0},
            {"name": "price_accuracy", "dimension": "accuracy", "column_name": "price", "threshold": 1.0, "config": json.dumps({"min": 0, "max": 10000})},
            {"name": "category_validity", "dimension": "validity", "column_name": "category", "threshold": 1.0, "config": json.dumps({"allowed": ["Electronics", "Books", "Clothing"]})},
        ]
    elif source_name == "corrupted":
        rules = [
            {"name": "id_completeness", "dimension": "completeness", "column_name": "id", "threshold": 0.95},
            {"name": "id_uniqueness", "dimension": "uniqueness", "column_name": "id", "threshold": 0.90},
            {"name": "email_completeness", "dimension": "completeness", "column_name": "email", "threshold": 0.90},
            {"name": "value_completeness", "dimension": "completeness", "column_name": "value", "threshold": 0.90},
            {"name": "age_accuracy", "dimension": "accuracy", "column_name": "age", "threshold": 0.90, "config": json.dumps({"min": 0, "max": 150})},
            {"name": "status_validity", "dimension": "validity", "column_name": "status", "threshold": 0.90, "config": json.dumps({"allowed": ["active", "inactive"]})},
        ]

    for r in rules:
        r["source_id"] = source_id
    return rules


def main() -> None:
    """Seed the database with sources, rules, and schedules."""
    engine = create_engine(DATABASE_URL)
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        # Clear existing test data
        session.query(Rule).delete()
        session.query(Schedule).delete()
        session.query(DataSource).delete()
        session.commit()

        total_rules = 0
        for src_data in SOURCES:
            source = DataSource(**src_data)
            session.add(source)
            session.flush()

            rules = build_rules(source.id, src_data["name"])
            for rule_data in rules:
                session.add(Rule(**rule_data))
                total_rules += 1

        # Add a sample schedule
        session.add(Schedule(
            name="Daily DQ Check",
            cron_expression="0 6 * * *",
            is_active=True,
        ))

        session.commit()
        print(f"Seeded {len(SOURCES)} sources, {total_rules} rules, 1 schedule")


if __name__ == "__main__":
    main()
