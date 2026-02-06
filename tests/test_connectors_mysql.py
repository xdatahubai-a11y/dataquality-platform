"""Tests for MySQL connector."""

from unittest.mock import MagicMock, patch

import pytest

from connectors.mysql import MySQLConnector


@pytest.fixture
def connector() -> MySQLConnector:
    return MySQLConnector()


class TestMySQLConnector:
    """Test suite for MySQLConnector."""

    def test_connect(self, connector: MySQLConnector) -> None:
        mock_mysql_mod = MagicMock()
        with patch.dict("sys.modules", {"mysql": MagicMock(), "mysql.connector": mock_mysql_mod}):
            connector.connect({"host": "localhost", "database": "testdb", "username": "u", "password": "p"})
        assert connector._connection is not None

    def test_test_connection_no_connection(self, connector: MySQLConnector) -> None:
        assert connector.test_connection() is False

    def test_test_connection_success(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        connector._connection = mock_conn
        assert connector.test_connection() is True

    def test_test_connection_failure(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_conn.cursor.side_effect = Exception("fail")
        connector._connection = mock_conn
        assert connector.test_connection() is False

    def test_read_data_not_connected(self, connector: MySQLConnector) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("table")

    def test_read_data_table(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("name",)]
        mock_cursor.fetchall.return_value = [(1, "alice")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        result = connector.read_data("users")
        assert result == [{"id": 1, "name": "alice"}]

    def test_read_data_with_limit(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",)]
        mock_cursor.fetchall.return_value = [(1,)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        connector.read_data("users", limit=5)
        call_args = mock_cursor.execute.call_args[0][0]
        assert "LIMIT 5" in call_args

    def test_read_data_sql_query(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("cnt",)]
        mock_cursor.fetchall.return_value = [(10,)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        result = connector.read_data("sql:SELECT COUNT(*) as cnt FROM t")
        assert result == [{"cnt": 10}]

    def test_list_tables(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("users",), ("orders",)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn
        connector._database = "testdb"

        assert connector.list_tables() == ["users", "orders"]

    def test_get_schema(self, connector: MySQLConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("id", "int"), ("name", "varchar")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn
        connector._database = "testdb"

        assert connector.get_schema("users") == {"id": "int", "name": "varchar"}

    def test_list_tables_not_connected(self, connector: MySQLConnector) -> None:
        assert connector.list_tables() == []

    def test_get_schema_not_connected(self, connector: MySQLConnector) -> None:
        assert connector.get_schema("t") == {}
