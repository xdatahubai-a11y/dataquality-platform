"""Tests for BigQuery connector."""

from unittest.mock import MagicMock, patch

import pytest


class TestBigQueryConnector:
    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def _make_connector(self):
        from connectors.bigquery import BigQueryConnector
        return BigQueryConnector()

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_connect_valid_config(self):
        connector = self._make_connector()
        connector.connect({"project_id": "my-project", "dataset": "my_dataset"})
        assert connector._client is not None
        assert connector._project_id == "my-project"
        assert connector._dataset == "my_dataset"

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_connect_with_credentials_path(self):
        with patch.dict("sys.modules", {
            "google.oauth2": MagicMock(),
            "google.oauth2.service_account": MagicMock(),
        }):
            connector = self._make_connector()
            connector.connect({
                "project_id": "my-project",
                "dataset": "ds",
                "credentials_path": "/path/to/creds.json",
            })
            assert connector._client is not None

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_test_connection_success(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        assert connector.test_connection() is True

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_test_connection_failure(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        connector._client.query.side_effect = Exception("fail")
        assert connector.test_connection() is False

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_test_connection_not_connected(self):
        connector = self._make_connector()
        assert connector.test_connection() is False

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_read_data_with_limit_and_columns(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        connector._project_id = "proj"
        connector._dataset = "ds"

        mock_row = MagicMock()
        mock_row.__iter__ = MagicMock(return_value=iter([("name", "Alice")]))
        dict_row = {"name": "Alice", "age": 30}
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([dict_row]))
        connector._client.query.return_value.result.return_value = mock_result

        result = connector.read_data("users", limit=10, columns=["name", "age"])
        call_args = connector._client.query.call_args[0][0]
        assert "name, age" in call_args
        assert "LIMIT 10" in call_args

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_read_data_sql_prefix(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        connector._client.query.return_value.result.return_value = iter([])

        connector.read_data("sql:SELECT * FROM my_table WHERE id = 1")
        call_args = connector._client.query.call_args[0][0]
        assert call_args == "SELECT * FROM my_table WHERE id = 1"

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_read_data_not_connected(self):
        connector = self._make_connector()
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("table")

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_list_tables(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        connector._project_id = "proj"
        connector._dataset = "ds"

        mock_table1 = MagicMock()
        mock_table1.table_id = "table_a"
        mock_table2 = MagicMock()
        mock_table2.table_id = "table_b"
        connector._client.list_tables.return_value = [mock_table1, mock_table2]

        result = connector.list_tables()
        assert result == ["table_a", "table_b"]

    @patch.dict("sys.modules", {"google": MagicMock(), "google.cloud": MagicMock(), "google.cloud.bigquery": MagicMock()})
    def test_get_schema(self):
        connector = self._make_connector()
        connector._client = MagicMock()
        connector._project_id = "proj"
        connector._dataset = "ds"

        field1 = MagicMock()
        field1.name = "id"
        field1.field_type = "INTEGER"
        field2 = MagicMock()
        field2.name = "name"
        field2.field_type = "STRING"

        mock_table = MagicMock()
        mock_table.schema = [field1, field2]
        connector._client.get_table.return_value = mock_table

        schema = connector.get_schema("users")
        assert schema == {"id": "INTEGER", "name": "STRING"}
