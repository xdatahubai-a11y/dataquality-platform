"""AWS Glue Data Catalog connector."""

from typing import Optional

from connectors.base import DataConnector


class GlueCatalogConnector(DataConnector):
    """Connector for AWS Glue Data Catalog metadata."""

    def __init__(self) -> None:
        self._client = None
        self._database: str = ""

    def connect(self, config: dict) -> None:
        """Connect to AWS Glue Data Catalog.

        Config keys: database, region, aws_access_key_id, aws_secret_access_key.
        Omit credentials for IAM role auth.
        """
        try:
            import boto3
        except ImportError:
            raise RuntimeError("boto3 package required")

        self._database = config["database"]

        session_kwargs: dict = {}
        if config.get("aws_access_key_id"):
            session_kwargs["aws_access_key_id"] = config["aws_access_key_id"]
            session_kwargs["aws_secret_access_key"] = config["aws_secret_access_key"]
        if config.get("region"):
            session_kwargs["region_name"] = config["region"]

        session = boto3.Session(**session_kwargs)
        self._client = session.client("glue")

    def test_connection(self) -> bool:
        """Test Glue connection by getting database metadata."""
        if not self._client:
            return False
        try:
            self._client.get_database(Name=self._database)
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read table metadata (columns) from Glue Catalog.

        Args:
            path: Table name in the configured database.
        """
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")

        response = self._client.get_table(DatabaseName=self._database, Name=path)
        table = response["Table"]
        col_list = table.get("StorageDescriptor", {}).get("Columns", [])
        partition_keys = table.get("PartitionKeys", [])

        data = []
        for col in col_list + partition_keys:
            row = {"name": col["Name"], "type": col["Type"], "comment": col.get("Comment", "")}
            data.append(row)

        if columns:
            data = [{k: row.get(k) for k in columns} for row in data]
        if limit:
            data = data[:limit]
        return data

    def list_tables(self) -> list[str]:
        """List tables in the configured Glue database."""
        if not self._client:
            return []
        response = self._client.get_tables(DatabaseName=self._database)
        return [t["Name"] for t in response.get("TableList", [])]

    def get_schema(self, path: str) -> dict[str, str]:
        """Get table schema from Glue Catalog."""
        if not self._client:
            return {}
        response = self._client.get_table(DatabaseName=self._database, Name=path)
        table = response["Table"]
        cols = table.get("StorageDescriptor", {}).get("Columns", [])
        partitions = table.get("PartitionKeys", [])
        return {col["Name"]: col["Type"] for col in cols + partitions}
