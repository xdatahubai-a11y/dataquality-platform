"""Tests for health endpoint."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock

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


def test_health_endpoint_returns_200():
    """Test that health endpoint returns 200 status code."""
    response = client.get("/api/health")
    assert response.status_code == 200


def test_health_endpoint_returns_correct_structure():
    """Test that health endpoint returns expected JSON structure."""
    response = client.get("/api/health")
    data = response.json()

    assert "status" in data
    assert "version" in data
    assert "database" in data
    assert data["status"] == "healthy"


def test_health_endpoint_version_not_empty():
    """Test that health endpoint returns non-empty version."""
    response = client.get("/api/health")
    data = response.json()

    assert data["version"]  # Should not be empty
    assert isinstance(data["version"], str)


def test_health_endpoint_database_connected():
    """Test that health endpoint shows database as connected when DB is healthy."""
    response = client.get("/api/health")
    data = response.json()

    assert data["database"] == "connected"


def test_health_endpoint_database_error():
    """Test that health endpoint shows database error when DB connection fails."""
    with patch('api.main.engine.connect') as mock_connect:
        # Mock database connection error
        mock_conn = MagicMock()
        mock_conn.__enter__.side_effect = Exception("Database connection failed")
        mock_connect.return_value = mock_conn

        response = client.get("/api/health")
        data = response.json()

        assert response.status_code == 200  # Health endpoint should still return 200
        assert data["status"] == "healthy"
        assert data["database"].startswith("error:")
        assert "Database connection failed" in data["database"]