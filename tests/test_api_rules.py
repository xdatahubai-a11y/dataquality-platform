"""Tests for rules API endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import engine
from api.models.database import Base


@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_rule():
    resp = client.post("/api/rules", json={
        "name": "test_completeness",
        "dimension": "completeness",
        "column_name": "email",
        "threshold": 95.0,
        "severity": "warning",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "test_completeness"
    assert data["dimension"] == "completeness"
    assert data["is_active"] is True


def test_list_rules():
    # Create two rules
    client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    client.post("/api/rules", json={"name": "r2", "dimension": "uniqueness"})
    resp = client.get("/api/rules")
    assert resp.status_code == 200
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 2


def test_get_rule():
    create_resp = client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    rule_id = create_resp.json()["id"]
    resp = client.get(f"/api/rules/{rule_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "r1"


def test_get_rule_not_found():
    resp = client.get("/api/rules/nonexistent-id")
    assert resp.status_code == 404


def test_update_rule():
    create_resp = client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    rule_id = create_resp.json()["id"]
    resp = client.put(f"/api/rules/{rule_id}", json={"name": "updated_name"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "updated_name"


def test_delete_rule():
    create_resp = client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    rule_id = create_resp.json()["id"]
    resp = client.delete(f"/api/rules/{rule_id}")
    assert resp.status_code == 204
    # Verify soft-deleted
    get_resp = client.get(f"/api/rules/{rule_id}")
    assert get_resp.json()["is_active"] is False


def test_filter_by_dimension():
    client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    client.post("/api/rules", json={"name": "r2", "dimension": "uniqueness"})
    resp = client.get("/api/rules?dimension=completeness")
    assert resp.json()["total"] == 1
