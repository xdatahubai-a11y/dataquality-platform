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
    assert data["skip"] == 0
    assert data["limit"] == 50


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


def test_pagination_with_skip_and_limit():
    """Test pagination using skip and limit parameters."""
    # Create 5 rules
    for i in range(5):
        client.post("/api/rules", json={"name": f"rule_{i}", "dimension": "completeness"})

    # Test default pagination
    resp = client.get("/api/rules")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 5
    assert data["skip"] == 0
    assert data["limit"] == 50

    # Test with limit=2
    resp = client.get("/api/rules?limit=2")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2

    # Test with skip=2, limit=2 (should get items 2-3)
    resp = client.get("/api/rules?skip=2&limit=2")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 2
    assert data["skip"] == 2
    assert data["limit"] == 2

    # Test with skip=4, limit=2 (should get only 1 item)
    resp = client.get("/api/rules?skip=4&limit=2")
    data = resp.json()
    assert data["total"] == 5
    assert len(data["items"]) == 1
    assert data["skip"] == 4
    assert data["limit"] == 2


def test_pagination_empty_result():
    """Test pagination when skip is beyond available items."""
    # Create 2 rules
    client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    client.post("/api/rules", json={"name": "r2", "dimension": "uniqueness"})

    # Skip beyond available items
    resp = client.get("/api/rules?skip=10")
    data = resp.json()
    assert data["total"] == 2
    assert len(data["items"]) == 0
    assert data["skip"] == 10
    assert data["limit"] == 50


def test_pagination_with_filters():
    """Test pagination combined with filters."""
    # Create rules with different dimensions
    for i in range(3):
        client.post("/api/rules", json={"name": f"comp_{i}", "dimension": "completeness"})
    for i in range(2):
        client.post("/api/rules", json={"name": f"uniq_{i}", "dimension": "uniqueness"})

    # Filter by dimension with pagination
    resp = client.get("/api/rules?dimension=completeness&limit=2")
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 2
    assert data["skip"] == 0
    assert data["limit"] == 2

    # Get remaining completeness rules
    resp = client.get("/api/rules?dimension=completeness&skip=2&limit=2")
    data = resp.json()
    assert data["total"] == 3
    assert len(data["items"]) == 1
    assert data["skip"] == 2
    assert data["limit"] == 2


def test_pagination_boundary_validation():
    """Test validation of skip and limit parameters."""
    # Test negative skip
    resp = client.get("/api/rules?skip=-1")
    assert resp.status_code == 422

    # Test zero limit
    resp = client.get("/api/rules?limit=0")
    assert resp.status_code == 422

    # Test limit above maximum
    resp = client.get("/api/rules?limit=101")
    assert resp.status_code == 422

    # Test valid boundary values
    resp = client.get("/api/rules?skip=0&limit=1")
    assert resp.status_code == 200

    resp = client.get("/api/rules?skip=0&limit=100")
    assert resp.status_code == 200


# Validation tests
def test_create_rule_invalid_dimension():
    """Test creating a rule with invalid dimension returns 422."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "banana",
    })
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "dimension" in error_detail["loc"]


def test_create_rule_invalid_operator():
    """Test creating a rule with invalid operator returns 422."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "completeness",
        "operator": "yolo",
    })
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "operator must be one of:" in error_detail["msg"]


def test_create_completeness_rule_invalid_threshold():
    """Test creating a completeness rule with threshold > 100 returns 422."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "completeness",
        "threshold": 150.0,
    })
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "must be between 0 and 100" in error_detail["msg"]


def test_create_uniqueness_rule_invalid_threshold():
    """Test creating a uniqueness rule with threshold > 100 returns 422."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "uniqueness",
        "threshold": 150.0,
    })
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "must be between 0 and 100" in error_detail["msg"]


def test_create_validity_rule_invalid_threshold():
    """Test creating a validity rule with threshold > 100 returns 422."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "validity",
        "threshold": 150.0,
    })
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "must be between 0 and 100" in error_detail["msg"]


def test_create_accuracy_rule_high_threshold_allowed():
    """Test creating an accuracy rule with threshold > 100 is allowed (not percentage-based)."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "accuracy",
        "threshold": 150.0,
    })
    assert resp.status_code == 201
    assert resp.json()["threshold"] == 150.0


def test_create_consistency_rule_high_threshold_allowed():
    """Test creating a consistency rule with threshold > 100 is allowed."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "consistency",
        "threshold": 200.0,
    })
    assert resp.status_code == 201
    assert resp.json()["threshold"] == 200.0


def test_create_timeliness_rule_high_threshold_allowed():
    """Test creating a timeliness rule with threshold > 100 is allowed."""
    resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "timeliness",
        "threshold": 500.0,
    })
    assert resp.status_code == 201
    assert resp.json()["threshold"] == 500.0


def test_update_rule_invalid_operator():
    """Test updating a rule with invalid operator returns 422."""
    create_resp = client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    rule_id = create_resp.json()["id"]

    resp = client.put(f"/api/rules/{rule_id}", json={"operator": "invalid"})
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "operator must be one of:" in error_detail["msg"]


def test_update_rule_invalid_threshold():
    """Test updating a percentage-based rule with invalid threshold returns 422."""
    create_resp = client.post("/api/rules", json={"name": "r1", "dimension": "completeness"})
    rule_id = create_resp.json()["id"]

    resp = client.put(f"/api/rules/{rule_id}", json={"threshold": 150.0})
    assert resp.status_code == 422
    error_detail = resp.json()["detail"][0]
    assert "must be between 0 and 100" in error_detail["msg"]


def test_create_rule_valid_operators():
    """Test all valid operators are accepted."""
    valid_operators = ["gte", "lte", "gt", "lt", "eq"]

    for i, operator in enumerate(valid_operators):
        resp = client.post("/api/rules", json={
            "name": f"test_rule_{i}",
            "dimension": "completeness",
            "operator": operator,
            "threshold": 90.0,
        })
        assert resp.status_code == 201
        assert resp.json()["operator"] == operator
