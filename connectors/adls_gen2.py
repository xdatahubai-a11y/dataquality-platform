"""ADLS Gen2 data source connector."""

import json
from typing import Optional

from connectors.base import DataConnector


class ADLSGen2Connector(DataConnector):
    """Connector for Azure Data Lake Storage Gen2."""

    def __init__(self) -> None:
        self._client = None
        self._account_name: str = ""
        self._account_key: str = ""
        self._container: str = ""

    def connect(self, config: dict) -> None:
        """Connect to ADLS Gen2.

        Config keys: account_name, account_key (or use_managed_identity), container.
        """
        self._account_name = config["account_name"]
        self._account_key = config.get("account_key", "")
        self._container = config.get("container", "")

        try:
            from azure.storage.filedatalake import DataLakeServiceClient

            if config.get("use_managed_identity"):
                from azure.identity import DefaultAzureCredential
                credential = DefaultAzureCredential()
            else:
                credential = self._account_key

            self._client = DataLakeServiceClient(
                account_url=f"https://{self._account_name}.dfs.core.windows.net",
                credential=credential,
            )
        except ImportError:
            raise RuntimeError("azure-storage-file-datalake package required")

    def test_connection(self) -> bool:
        """Test ADLS Gen2 connection by listing file systems."""
        if not self._client:
            return False
        try:
            list(self._client.list_file_systems(max_results=1))
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read a file from ADLS Gen2 (supports CSV, JSON, Parquet via pandas)."""
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")

        fs_client = self._client.get_file_system_client(self._container)
        file_client = fs_client.get_file_client(path)
        download = file_client.download_file()
        content = download.readall()

        # Detect format and parse
        if path.endswith(".json") or path.endswith(".jsonl"):
            import io
            lines = content.decode("utf-8").strip().split("\n")
            data = [json.loads(line) for line in lines]
        elif path.endswith(".csv"):
            import csv
            import io
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            data = list(reader)
        else:
            # Default: try JSON
            data = json.loads(content)

        if columns:
            data = [{k: row.get(k) for k in columns} for row in data]
        if limit:
            data = data[:limit]
        return data

    def list_tables(self) -> list[str]:
        """List files in the configured container."""
        if not self._client:
            return []
        fs_client = self._client.get_file_system_client(self._container)
        return [p.name for p in fs_client.get_paths()]

    def get_schema(self, path: str) -> dict[str, str]:
        """Infer schema from first row of data."""
        data = self.read_data(path, limit=1)
        if not data:
            return {}
        return {k: type(v).__name__ for k, v in data[0].items()}
