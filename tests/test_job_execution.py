"""Tests for job execution and DQ check processing."""

import json
import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import engine
from api.models.database import Base

# Create a test database for each test
@pytest.fixture(autouse=True)
def setup_db():
    """Create tables before each test and drop after."""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_job_execution_with_sqlite_source():
    """Test successful job execution with SQLite source and rules."""
    # Create a SQLite data source
    source_resp = client.post("/api/sources", json={
        "name": "test_sqlite_source",
        "type": "sqlite",
        "connection_config": {
            "database": ":memory:"  # Use in-memory SQLite for testing
        }
    })
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    # Create some rules for this source
    rule1_resp = client.post("/api/rules", json={
        "name": "completeness_check",
        "dimension": "completeness",
        "source_id": source_id,
        "column_name": "name",
        "threshold": 80.0,
        "operator": "gte",
        "severity": "warning"
    })
    assert rule1_resp.status_code == 201
    rule1_id = rule1_resp.json()["id"]

    rule2_resp = client.post("/api/rules", json={
        "name": "uniqueness_check",
        "dimension": "uniqueness",
        "source_id": source_id,
        "column_name": "id",
        "threshold": 100.0,
        "operator": "gte",
        "severity": "critical"
    })
    assert rule2_resp.status_code == 201
    rule2_id = rule2_resp.json()["id"]

    # Submit a job with specific rule IDs
    job_resp = client.post("/api/jobs", json={
        "source_id": source_id,
        "rule_ids": [rule1_id, rule2_id],
        "parameters": {
            "limit": 1000
        }
    })

    # Should fail initially because in-memory SQLite won't have any tables
    assert job_resp.status_code == 201
    job = job_resp.json()

    # The job should exist and have a status
    assert "id" in job
    assert job["source_id"] == source_id
    assert job["status"] in ["running", "failed"]  # Could be either depending on execution timing


def test_job_execution_with_missing_source():
    """Test job submission with non-existent source."""
    job_resp = client.post("/api/jobs", json={
        "source_id": "nonexistent-source-id",
        "rule_ids": [],
        "parameters": {}
    })

    # Job should be created but will fail during execution
    assert job_resp.status_code == 201
    job = job_resp.json()

    # Check the job details - it should have failed
    job_detail_resp = client.get(f"/api/jobs/{job['id']}")
    assert job_detail_resp.status_code == 200
    job_detail = job_detail_resp.json()
    assert job_detail["status"] == "failed"
    assert "not found" in job_detail.get("error_message", "").lower()


def test_job_execution_with_no_rules():
    """Test job execution when no active rules are found."""
    # Create a data source
    source_resp = client.post("/api/sources", json={
        "name": "test_source_no_rules",
        "type": "sqlite",
        "connection_config": {
            "database": ":memory:"
        }
    })
    assert source_resp.status_code == 201
    source_id = source_resp.json()["id"]

    # Submit job without any rules
    job_resp = client.post("/api/jobs", json={
        "source_id": source_id,
        "rule_ids": [],  # Empty rule list
        "parameters": {}
    })

    assert job_resp.status_code == 201
    job = job_resp.json()

    # Job should fail because no rules found
    job_detail_resp = client.get(f"/api/jobs/{job['id']}")
    job_detail = job_detail_resp.json()
    assert job_detail["status"] == "failed"
    assert "no active rules" in job_detail.get("error_message", "").lower()


def test_job_list_and_filtering():
    """Test job listing and filtering functionality."""
    # Create a data source
    source_resp = client.post("/api/sources", json={
        "name": "test_source",
        "type": "sqlite",
        "connection_config": {"database": ":memory:"}
    })
    source_id = source_resp.json()["id"]

    # Submit multiple jobs
    for i in range(3):
        client.post("/api/jobs", json={
            "source_id": source_id,
            "parameters": {"test_job": i}
        })

    # Test job listing
    list_resp = client.get("/api/jobs")
    assert list_resp.status_code == 200
    job_list = list_resp.json()
    assert job_list["total"] == 3
    assert len(job_list["items"]) == 3

    # Test filtering by source
    filtered_resp = client.get(f"/api/jobs?source_id={source_id}")
    assert filtered_resp.status_code == 200
    filtered_list = filtered_resp.json()
    assert filtered_list["total"] == 3

    # Test filtering by status
    status_resp = client.get("/api/jobs?status=failed")
    assert status_resp.status_code == 200


def test_job_retry_functionality():
    """Test job retry functionality."""
    # Create a data source
    source_resp = client.post("/api/sources", json={
        "name": "test_retry_source",
        "type": "sqlite",
        "connection_config": {"database": ":memory:"}
    })
    source_id = source_resp.json()["id"]

    # Submit a job that will fail
    job_resp = client.post("/api/jobs", json={
        "source_id": source_id,
        "parameters": {}
    })
    original_job_id = job_resp.json()["id"]

    # Wait for it to complete/fail, then retry
    retry_resp = client.post(f"/api/jobs/{original_job_id}/retry")
    assert retry_resp.status_code == 200

    new_job = retry_resp.json()
    assert new_job["id"] != original_job_id
    assert new_job["source_id"] == source_id
    assert new_job["status"] in ["running", "failed", "pending"]


def test_get_nonexistent_job():
    """Test getting a job that doesn't exist."""
    resp = client.get("/api/jobs/nonexistent-job-id")
    assert resp.status_code == 404


def test_retry_nonexistent_job():
    """Test retrying a job that doesn't exist."""
    resp = client.post("/api/jobs/nonexistent-job-id/retry")
    assert resp.status_code == 404


def test_job_execution_creates_results():
    """Test that job execution creates DQResult records."""
    # This test would need actual data in the SQLite database to properly test
    # For now, we verify the job structure and that results relationship exists

    # Create a source and rule
    source_resp = client.post("/api/sources", json={
        "name": "test_results_source",
        "type": "sqlite",
        "connection_config": {"database": ":memory:"}
    })
    source_id = source_resp.json()["id"]

    rule_resp = client.post("/api/rules", json={
        "name": "test_rule",
        "dimension": "completeness",
        "source_id": source_id,
        "column_name": "test_column",
        "threshold": 50.0
    })
    rule_id = rule_resp.json()["id"]

    # Submit job
    job_resp = client.post("/api/jobs", json={
        "source_id": source_id,
        "rule_ids": [rule_id]
    })

    assert job_resp.status_code == 201
    job = job_resp.json()

    # Verify job was created with expected structure
    assert job["source_id"] == source_id
    assert "started_at" in job  # Should have started_at timestamp
    assert job["total_rules"] == 0  # Will be 0 initially, updated after execution
    assert job["passed_rules"] == 0
    assert job["failed_rules"] == 0