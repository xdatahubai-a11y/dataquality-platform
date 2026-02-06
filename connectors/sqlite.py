"""SQLite connector for local data quality testing.

Uses sqlite3 stdlib module for zero-dependency local testing.
"""

import sqlite3
from typing import Optional

from connectors.base import DataConnector


class SQLiteConnector(DataConnector):
    """SQLite connector following the DataConnector interface."""

    def __init__(self) -> None:
        self._conn: Optional[sqlite3.Connection] = None
        self._db_path: str = ""

    def connect(self, config: dict) -> None:
        """Connect to a SQLite database file.

        Args:
            config: Must contain 'database' key with path to .db file.
        """
        self._db_path = config["database"]
        self._conn = sqlite3.connect(self._db_path)
        self._conn.row_factory = sqlite3.Row

    def test_connection(self) -> bool:
        """Test if the SQLite connection is valid."""
        if not self._conn:
            return False
        try:
            self._conn.execute("SELECT 1")
            return True
        except sqlite3.Error:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from a SQLite table.

        Args:
            path: Table name.
            limit: Max rows to return.
            columns: Specific columns to select.

        Returns:
            List of row dictionaries.
        """
        if not self._conn:
            raise RuntimeError("Not connected. Call connect() first.")

        cols = ", ".join(columns) if columns else "*"
        query = f"SELECT {cols} FROM {path}"  # noqa: S608
        if limit:
            query += f" LIMIT {limit}"

        cursor = self._conn.execute(query)
        col_names = [desc[0] for desc in cursor.description]
        return [dict(zip(col_names, row)) for row in cursor.fetchall()]

    def list_tables(self) -> list[str]:
        """List all tables in the SQLite database."""
        if not self._conn:
            raise RuntimeError("Not connected.")
        cursor = self._conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        return [row[0] for row in cursor.fetchall()]

    def get_schema(self, path: str) -> dict[str, str]:
        """Get column names and types for a table."""
        if not self._conn:
            raise RuntimeError("Not connected.")
        cursor = self._conn.execute(f"PRAGMA table_info({path})")
        return {row[1]: row[2] for row in cursor.fetchall()}

    def close(self) -> None:
        """Close the connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
