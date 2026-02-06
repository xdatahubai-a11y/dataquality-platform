"""Shared test fixtures for DataQuality Platform tests."""

import json
import os
import sys

import pytest

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Use SQLite for tests
os.environ["DQ_DATABASE_URL"] = "sqlite:///./test_dataquality.db"


@pytest.fixture
def sample_data() -> list[dict]:
    """Sample dataset for testing DQ dimensions."""
    return [
        {"id": 1, "name": "Alice", "email": "alice@example.com", "age": 30, "status": "active", "created_at": "2024-01-01", "updated_at": "2024-01-02"},
        {"id": 2, "name": "Bob", "email": "bob@example.com", "age": 25, "status": "active", "created_at": "2024-01-01", "updated_at": "2024-01-03"},
        {"id": 3, "name": None, "email": None, "age": -5, "status": "unknown", "created_at": "2024-01-05", "updated_at": "2024-01-02"},
        {"id": 4, "name": "Diana", "email": "not-an-email", "age": 200, "status": "active", "created_at": "2024-01-01", "updated_at": "2024-01-04"},
        {"id": 4, "name": "Eve", "email": "eve@test.com", "age": 45, "status": "inactive", "created_at": "2024-01-01", "updated_at": "2024-01-01"},
    ]


@pytest.fixture
def sample_rules_yaml(tmp_path) -> str:
    """Create a temporary rules YAML file."""
    rules = {
        "source": "test_data",
        "checks": [
            {"name": "name_completeness", "dimension": "completeness", "column": "name", "threshold": 80.0, "operator": "gte"},
            {"name": "id_uniqueness", "dimension": "uniqueness", "column": "id", "threshold": 100.0, "operator": "gte"},
            {"name": "email_validity", "dimension": "validity", "column": "email", "threshold": 80.0, "operator": "gte", "config": {"format": "email"}},
        ],
    }
    import yaml
    path = tmp_path / "test_rules.yaml"
    path.write_text(yaml.dump(rules))
    return str(path)
