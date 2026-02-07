"""Tests for SQLite connector batch/streaming reads."""

import sqlite3

import pytest

from connectors.sqlite import SQLiteConnector


@pytest.fixture
def small_db(tmp_path):
    """Create a small SQLite DB with 50 rows."""
    db_path = str(tmp_path / "test.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE data (id INTEGER, value TEXT)")
    conn.executemany("INSERT INTO data VALUES (?, ?)", [(i, f"v{i}") for i in range(50)])
    conn.commit()
    conn.close()
    return db_path


@pytest.fixture
def large_db(tmp_path):
    """Create a 100K row SQLite DB."""
    db_path = str(tmp_path / "large.db")
    conn = sqlite3.connect(db_path)
    conn.execute("CREATE TABLE big (id INTEGER, name TEXT, score REAL)")
    conn.executemany(
        "INSERT INTO big VALUES (?, ?, ?)",
        [(i, f"name_{i}", i * 0.1) for i in range(100_000)],
    )
    conn.commit()
    conn.close()
    return db_path


class TestReadDataWithBatchSize:
    def test_read_data_default_batch(self, small_db):
        c = SQLiteConnector()
        c.connect({"database": small_db})
        rows = c.read_data("data")
        assert len(rows) == 50
        assert rows[0] == {"id": 0, "value": "v0"}
        c.close()

    def test_read_data_custom_batch(self, small_db):
        c = SQLiteConnector(batch_size=10)
        c.connect({"database": small_db})
        rows = c.read_data("data")
        assert len(rows) == 50
        assert all(isinstance(r, dict) for r in rows)
        c.close()


class TestBackwardCompatibility:
    def test_returns_list_of_dicts(self, small_db):
        c = SQLiteConnector()
        c.connect({"database": small_db})
        result = c.read_data("data")
        assert isinstance(result, list)
        assert all(isinstance(r, dict) for r in result)
        assert set(result[0].keys()) == {"id", "value"}
        c.close()


class TestReadDataIterator:
    def test_iterator_yields_batches(self, small_db):
        c = SQLiteConnector(batch_size=20)
        c.connect({"database": small_db})
        batches = list(c.read_data_iterator("data"))
        assert len(batches) == 3  # 20+20+10
        assert len(batches[0]) == 20
        assert len(batches[2]) == 10
        c.close()

    def test_iterator_custom_batch_size(self, small_db):
        c = SQLiteConnector(batch_size=7)
        c.connect({"database": small_db})
        batches = list(c.read_data_iterator("data"))
        total = sum(len(b) for b in batches)
        assert total == 50
        assert all(len(b) <= 7 for b in batches)
        c.close()


class TestLargeDataset:
    def test_large_dataset_read(self, large_db):
        c = SQLiteConnector(batch_size=10000)
        c.connect({"database": large_db})
        rows = c.read_data("big")
        assert len(rows) == 100_000
        assert rows[0]["id"] == 0
        assert rows[-1]["id"] == 99_999
        c.close()
