"""Tests for the SQLite connector."""

import sqlite3
import tempfile
from pathlib import Path

import pytest

from connectors.sqlite import SQLiteConnector


@pytest.fixture
def test_db(tmp_path: Path) -> str:
    """Create a temporary SQLite database for testing."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE users (id INTEGER, name TEXT, email TEXT)")
    conn.executemany(
        "INSERT INTO users VALUES (?, ?, ?)",
        [(1, "Alice", "alice@test.com"), (2, "Bob", None), (3, "Carol", "carol@test.com")],
    )
    conn.commit()
    conn.close()
    return db_path


def test_connect_and_test(test_db: str) -> None:
    """Test connection establishment and validation."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    assert c.test_connection() is True
    c.close()


def test_list_tables(test_db: str) -> None:
    """Test listing tables."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    assert "users" in c.list_tables()
    c.close()


def test_read_data(test_db: str) -> None:
    """Test reading data returns list of dicts."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    data = c.read_data("users")
    assert len(data) == 3
    assert data[0]["name"] == "Alice"
    c.close()


def test_read_data_with_limit(test_db: str) -> None:
    """Test reading with a row limit."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    data = c.read_data("users", limit=1)
    assert len(data) == 1
    c.close()


def test_read_data_with_columns(test_db: str) -> None:
    """Test reading specific columns."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    data = c.read_data("users", columns=["name"])
    assert list(data[0].keys()) == ["name"]
    c.close()


def test_get_schema(test_db: str) -> None:
    """Test schema retrieval."""
    c = SQLiteConnector()
    c.connect({"database": test_db})
    schema = c.get_schema("users")
    assert "id" in schema
    assert "name" in schema
    c.close()


def test_not_connected_raises() -> None:
    """Test that operations without connect() raise errors."""
    c = SQLiteConnector()
    with pytest.raises(RuntimeError):
        c.read_data("users")
