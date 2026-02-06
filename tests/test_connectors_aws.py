"""Tests for AWS connectors (S3, Redshift, Glue Catalog)."""

from unittest.mock import MagicMock, patch

import pytest

from connectors.glue_catalog import GlueCatalogConnector
from connectors.redshift import RedshiftConnector
from connectors.s3 import S3Connector


# === S3 Connector Tests ===

class TestS3Connector:
    """Test suite for S3Connector."""

    @pytest.fixture
    def connector(self) -> S3Connector:
        return S3Connector()

    def test_connect(self, connector: S3Connector) -> None:
        mock_boto3 = MagicMock()
        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            connector.connect({"bucket": "my-bucket", "region": "us-east-1"})
        assert connector._client is not None
        assert connector._bucket == "my-bucket"

    def test_test_connection_no_client(self, connector: S3Connector) -> None:
        assert connector.test_connection() is False

    def test_test_connection_success(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        assert connector.test_connection() is True

    def test_test_connection_failure(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._client.head_bucket.side_effect = Exception("no")
        connector._bucket = "b"
        assert connector.test_connection() is False

    def test_read_data_not_connected(self, connector: S3Connector) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("file.csv")

    def test_read_data_csv(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        body = MagicMock()
        body.read.return_value = b"id,name\n1,alice\n2,bob"
        connector._client.get_object.return_value = {"Body": body}

        result = connector.read_data("data.csv")
        assert len(result) == 2
        assert result[0]["name"] == "alice"

    def test_read_data_json(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        body = MagicMock()
        body.read.return_value = b'[{"id": 1}]'
        connector._client.get_object.return_value = {"Body": body}

        result = connector.read_data("data.json")
        assert result == [{"id": 1}]

    def test_read_data_jsonl(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        body = MagicMock()
        body.read.return_value = b'{"a":1}\n{"a":2}'
        connector._client.get_object.return_value = {"Body": body}

        result = connector.read_data("data.jsonl")
        assert len(result) == 2

    def test_read_data_with_prefix(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        connector._prefix = "raw"
        body = MagicMock()
        body.read.return_value = b'[{"x":1}]'
        connector._client.get_object.return_value = {"Body": body}

        connector.read_data("data.json")
        call_args = connector._client.get_object.call_args
        assert call_args[1]["Key"] == "raw/data.json"

    def test_list_tables(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        connector._client.list_objects_v2.return_value = {
            "Contents": [{"Key": "a.csv"}, {"Key": "b.json"}]
        }
        assert connector.list_tables() == ["a.csv", "b.json"]

    def test_get_schema(self, connector: S3Connector) -> None:
        connector._client = MagicMock()
        connector._bucket = "b"
        body = MagicMock()
        body.read.return_value = b'[{"id": 1, "name": "x"}]'
        connector._client.get_object.return_value = {"Body": body}

        schema = connector.get_schema("data.json")
        assert schema == {"id": "int", "name": "str"}


# === Redshift Connector Tests ===

class TestRedshiftConnector:
    """Test suite for RedshiftConnector."""

    @pytest.fixture
    def connector(self) -> RedshiftConnector:
        return RedshiftConnector()

    def test_test_connection_no_connection(self, connector: RedshiftConnector) -> None:
        assert connector.test_connection() is False

    def test_test_connection_success(self, connector: RedshiftConnector) -> None:
        connector._connection = MagicMock()
        assert connector.test_connection() is True

    def test_read_data_not_connected(self, connector: RedshiftConnector) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("table")

    def test_read_data(self, connector: RedshiftConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.description = [("id",), ("val",)]
        mock_cursor.fetchall.return_value = [(1, "a")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        result = connector.read_data("t")
        assert result == [{"id": 1, "val": "a"}]

    def test_list_tables(self, connector: RedshiftConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("public.t1",)]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        assert connector.list_tables() == ["public.t1"]

    def test_get_schema(self, connector: RedshiftConnector) -> None:
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_cursor.fetchall.return_value = [("id", "integer")]
        mock_conn.cursor.return_value = mock_cursor
        connector._connection = mock_conn

        assert connector.get_schema("t") == {"id": "integer"}

    def test_list_tables_not_connected(self, connector: RedshiftConnector) -> None:
        assert connector.list_tables() == []


# === Glue Catalog Connector Tests ===

class TestGlueCatalogConnector:
    """Test suite for GlueCatalogConnector."""

    @pytest.fixture
    def connector(self) -> GlueCatalogConnector:
        return GlueCatalogConnector()

    def test_connect(self, connector: GlueCatalogConnector) -> None:
        mock_boto3 = MagicMock()
        with patch.dict("sys.modules", {"boto3": mock_boto3}):
            connector.connect({"database": "mydb", "region": "us-east-1"})
        assert connector._client is not None
        assert connector._database == "mydb"

    def test_test_connection_no_client(self, connector: GlueCatalogConnector) -> None:
        assert connector.test_connection() is False

    def test_test_connection_success(self, connector: GlueCatalogConnector) -> None:
        connector._client = MagicMock()
        connector._database = "db"
        assert connector.test_connection() is True

    def test_read_data_not_connected(self, connector: GlueCatalogConnector) -> None:
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("table")

    def test_read_data(self, connector: GlueCatalogConnector) -> None:
        connector._client = MagicMock()
        connector._database = "db"
        connector._client.get_table.return_value = {
            "Table": {
                "StorageDescriptor": {
                    "Columns": [{"Name": "id", "Type": "int", "Comment": "PK"}]
                },
                "PartitionKeys": [{"Name": "dt", "Type": "string"}],
            }
        }

        result = connector.read_data("t")
        assert len(result) == 2
        assert result[0]["name"] == "id"
        assert result[1]["name"] == "dt"

    def test_list_tables(self, connector: GlueCatalogConnector) -> None:
        connector._client = MagicMock()
        connector._database = "db"
        connector._client.get_tables.return_value = {
            "TableList": [{"Name": "t1"}, {"Name": "t2"}]
        }
        assert connector.list_tables() == ["t1", "t2"]

    def test_get_schema(self, connector: GlueCatalogConnector) -> None:
        connector._client = MagicMock()
        connector._database = "db"
        connector._client.get_table.return_value = {
            "Table": {
                "StorageDescriptor": {
                    "Columns": [{"Name": "id", "Type": "int"}]
                },
                "PartitionKeys": [],
            }
        }
        assert connector.get_schema("t") == {"id": "int"}

    def test_list_tables_not_connected(self, connector: GlueCatalogConnector) -> None:
        assert connector.list_tables() == []

    def test_get_schema_not_connected(self, connector: GlueCatalogConnector) -> None:
        assert connector.get_schema("t") == {}
