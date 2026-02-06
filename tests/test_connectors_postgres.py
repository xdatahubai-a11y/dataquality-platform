"""Tests for PostgreSQL connector."""

from unittest.mock import MagicMock, patch

import pytest

from connectors.postgresql import PostgreSQLConnector


@pytest.fixture
def connector() -> PostgreSQLConnector:
    return PostgreSQLConnector()


class TestPostgreSQLConnector:
    """Test suite for PostgreSQLConnector."""

    def test_connect_with_params(self, connector: PostgreSQLConnector) -> None:
        mock_pg = MagicMock()
        with patch.dict("sys.modules", {"psycopg2": mock_pg}):
            connector.connect({"host": "localhost", "port": 5432, "database": "testdb", "username": "u", "password": "p"})
        assert connector._connection is not None

    def test_connect_with_connection_string(self, connector: PostgreSQLConnector) -> None:
        mock_pg = MagicMock()
        with patch.dict("sys.modules", {"psycopg2": mock_pg}):
            connector.connect({"connection_string": "postgresql://u:p@localhost/db"})
        mock_pg.connect.assert_called_once_with("postgresql://u:p@localhost/db")

    def test_test_connection_no_connection(self, connector: PostgreSQLConnector) -> None:
        assert connector.test_connection() is False

    def test_test_connection_success(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        connector._connection = mock_conn
        assert connector.test_connection() is True

    def test_test_connection_failure(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("fail")
        connector._connection = mock_conn
        assert connector.test_connection() is False

    def test_read_data_not_connected(self, connector: PostgreSQLConnector) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("table")

    def test_read_data_table(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "alice"), (2, "bob")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        result = connector.read_data("users", limit=10)
        assert len(result) == 2
        assert result[0] == {"id": 1, "name": "alice"}

    def test_read_data_sql_query(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("cnt",)]
        mock_cursor.fetchall.return_value = [(42,)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        result = connector.read_data("sql:SELECT COUNT(*) as cnt FROM users")
        assert result == [{"cnt": 42}]

    def test_list_tables(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("public.users",), ("public.orders",)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        tables = connector.list_tables()
        assert tables == ["public.users", "public.orders"]

    def test_get_schema(self, connector: PostgreSQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("id", "integer"), ("name", "varchar")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        schema = connector.get_schema("users")
        assert schema == {"id": "integer", "name": "varchar"}

    def test_list_tables_not_connected(self, connector: PostgreSQLConnector) -> None:
        assert connector.list_tables() == []

    def test_get_schema_not_connected(self, connector: PostgreSQLConnector) -> None:
        assert connector.get_schema("t") == {}
