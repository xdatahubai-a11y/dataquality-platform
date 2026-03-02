"""Tests for data sources API endpoints."""

import pytest
from fastapi.testclient import TestClient

from api.main import app
from api.dependencies import engine
from api.models.database import Base


@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


client = TestClient(app)


def test_create_source():
    resp = client.post("/api/sources", json={
        "name": "Test ADLS",
        "type": "adls_gen2",
        "connection_config": {"account_name": "testaccount", "container": "data"},
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["name"] == "Test ADLS"
    assert data["type"] == "adls_gen2"


def test_list_sources():
    client.post("/api/sources", json={"name": "s1", "type": "adls_gen2", "connection_config": {}})
    client.post("/api/sources", json={"name": "s2", "type": "sql_server", "connection_config": {}})
    resp = client.get("/api/sources")
    assert resp.status_code == 200
    assert resp.json()["total"] == 2


def test_get_source():
    create_resp = client.post("/api/sources", json={"name": "s1", "type": "delta_table", "connection_config": {}})
    source_id = create_resp.json()["id"]
    resp = client.get(f"/api/sources/{source_id}")
    assert resp.status_code == 200
    assert resp.json()["name"] == "s1"


def test_update_source():
    create_resp = client.post("/api/sources", json={"name": "s1", "type": "adls_gen2", "connection_config": {}})
    source_id = create_resp.json()["id"]
    resp = client.put(f"/api/sources/{source_id}", json={"name": "updated"})
    assert resp.status_code == 200
    assert resp.json()["name"] == "updated"


def test_delete_source():
    create_resp = client.post("/api/sources", json={"name": "s1", "type": "adls_gen2", "connection_config": {}})
    source_id = create_resp.json()["id"]
    resp = client.delete(f"/api/sources/{source_id}")
    assert resp.status_code == 204


def test_test_connection():
    create_resp = client.post("/api/sources", json={"name": "s1", "type": "adls_gen2", "connection_config": {}})
    source_id = create_resp.json()["id"]
    resp = client.post(f"/api/sources/{source_id}/test")
    assert resp.status_code == 200
    # Should return success=false due to missing/invalid config for ADLS
    assert resp.json()["success"] is False


def test_connection_sqlite_success(tmp_path):
    """Test connection with a valid SQLite source."""
    # Create a temporary SQLite database
    db_path = tmp_path / "test.db"
    import sqlite3
    conn = sqlite3.connect(str(db_path))
    conn.execute("CREATE TABLE test_table (id INTEGER PRIMARY KEY, name TEXT)")
    conn.commit()
    conn.close()

    # Create a SQLite source
    create_resp = client.post("/api/sources", json={
        "name": "Test SQLite",
        "type": "sqlite",
        "connection_config": {"database": str(db_path)},
    })
    assert create_resp.status_code == 201
    source_id = create_resp.json()["id"]

    # Test the connection
    resp = client.post(f"/api/sources/{source_id}/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    assert "Successfully connected to Test SQLite" in data["message"]


def test_connection_sqlite_invalid_path():
    """Test connection with an invalid SQLite database path."""
    create_resp = client.post("/api/sources", json={
        "name": "Invalid SQLite",
        "type": "sqlite",
        "connection_config": {"database": "/nonexistent/path/test.db"},
    })
    assert create_resp.status_code == 201
    source_id = create_resp.json()["id"]

    # Test the connection - should fail
    resp = client.post(f"/api/sources/{source_id}/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert "error" in data


def test_connection_nonexistent_source():
    """Test connection with a non-existent source (404)."""
    resp = client.post("/api/sources/nonexistent-id/test")
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Data source not found"


def test_connection_unsupported_type():
    """Test connection with unsupported source type."""
    # This test might not be possible with current schema validation,
    # but we can test the error handling path by using an invalid config
    create_resp = client.post("/api/sources", json={
        "name": "Test MySQL",
        "type": "mysql",
        "connection_config": {},  # Missing required config
    })
    assert create_resp.status_code == 201
    source_id = create_resp.json()["id"]

    # Test the connection - should fail due to missing config
    resp = client.post(f"/api/sources/{source_id}/test")
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is False
    assert "error" in data
