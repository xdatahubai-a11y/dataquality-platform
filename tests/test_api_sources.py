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
    assert resp.json()["status"] == "ok"
