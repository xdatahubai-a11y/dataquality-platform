"""BigQuery data source connector."""

from typing import Optional

from connectors.base import DataConnector


class BigQueryConnector(DataConnector):
    """Connector for Google BigQuery via google-cloud-bigquery."""

    def __init__(self) -> None:
        self._client = None
        self._dataset: str = ""
        self._project_id: str = ""

    def connect(self, config: dict) -> None:
        """Connect to BigQuery.

        Config keys: project_id, credentials_path (optional), dataset.
        """
        try:
            from google.cloud import bigquery
        except ImportError:
            raise RuntimeError("google-cloud-bigquery package required")

        self._project_id = config["project_id"]
        self._dataset = config.get("dataset", "")

        credentials_path = config.get("credentials_path")
        if credentials_path:
            from google.oauth2 import service_account

            credentials = service_account.Credentials.from_service_account_file(
                credentials_path
            )
            self._client = bigquery.Client(
                project=self._project_id, credentials=credentials
            )
        else:
            self._client = bigquery.Client(project=self._project_id)

    def test_connection(self) -> bool:
        """Test BigQuery connection."""
        if not self._client:
            return False
        try:
            query_job = self._client.query("SELECT 1")
            query_job.result()
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from a BigQuery table or query.

        Args:
            path: Table name or SQL query (prefixed with 'sql:').
        """
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")

        if path.startswith("sql:"):
            query = path[4:]
        else:
            cols = ", ".join(columns) if columns else "*"
            table_ref = f"`{self._project_id}.{self._dataset}.{path}`"
            query = f"SELECT {cols} FROM {table_ref}"
            if limit:
                query += f" LIMIT {limit}"

        query_job = self._client.query(query)
        rows = query_job.result()

        return [dict(row) for row in rows]

    def list_tables(self) -> list[str]:
        """List tables in the connected dataset."""
        if not self._client:
            return []
        dataset_ref = f"{self._project_id}.{self._dataset}"
        tables = self._client.list_tables(dataset_ref)
        return [table.table_id for table in tables]

    def get_schema(self, path: str) -> dict[str, str]:
        """Get table schema from BigQuery."""
        if not self._client:
            return {}
        table_ref = f"{self._project_id}.{self._dataset}.{path}"
        table = self._client.get_table(table_ref)
        return {field.name: field.field_type for field in table.schema}
