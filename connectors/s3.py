"""AWS S3 data source connector."""

import io
import json
from typing import Optional

from connectors.base import DataConnector


class S3Connector(DataConnector):
    """Connector for AWS S3 buckets (CSV, JSON, Parquet)."""

    def __init__(self) -> None:
        self._client = None
        self._bucket: str = ""
        self._prefix: str = ""

    def connect(self, config: dict) -> None:
        """Connect to AWS S3.

        Config keys: bucket, prefix, region, aws_access_key_id, aws_secret_access_key.
        Omit credentials for IAM role auth.
        """
        try:
            import boto3
        except ImportError:
            raise RuntimeError("boto3 package required")

        self._bucket = config["bucket"]
        self._prefix = config.get("prefix", "")

        session_kwargs: dict = {}
        if config.get("aws_access_key_id"):
            session_kwargs["aws_access_key_id"] = config["aws_access_key_id"]
            session_kwargs["aws_secret_access_key"] = config["aws_secret_access_key"]
        if config.get("region"):
            session_kwargs["region_name"] = config["region"]

        session = boto3.Session(**session_kwargs)
        self._client = session.client("s3")

    def test_connection(self) -> bool:
        """Test S3 connection by listing bucket."""
        if not self._client:
            return False
        try:
            self._client.head_bucket(Bucket=self._bucket)
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read a file from S3 (CSV, JSON/JSONL, Parquet).

        Args:
            path: S3 key (relative to prefix).
        """
        if not self._client:
            raise RuntimeError("Not connected. Call connect() first.")

        full_key = f"{self._prefix}/{path}".lstrip("/") if self._prefix else path
        response = self._client.get_object(Bucket=self._bucket, Key=full_key)
        content = response["Body"].read()

        data = self._parse_content(content, full_key)

        if columns:
            data = [{k: row.get(k) for k in columns} for row in data]
        if limit:
            data = data[:limit]
        return data

    def _parse_content(self, content: bytes, key: str) -> list[dict]:
        """Parse file content based on extension."""
        if key.endswith(".csv"):
            import csv
            reader = csv.DictReader(io.StringIO(content.decode("utf-8")))
            return list(reader)
        elif key.endswith(".parquet"):
            import pyarrow.parquet as pq
            table = pq.read_table(io.BytesIO(content))
            return table.to_pylist()
        elif key.endswith(".jsonl"):
            lines = content.decode("utf-8").strip().split("\n")
            return [json.loads(line) for line in lines]
        else:
            return json.loads(content)

    def list_tables(self) -> list[str]:
        """List files in the configured bucket/prefix."""
        if not self._client:
            return []
        kwargs: dict = {"Bucket": self._bucket}
        if self._prefix:
            kwargs["Prefix"] = self._prefix
        response = self._client.list_objects_v2(**kwargs)
        return [obj["Key"] for obj in response.get("Contents", [])]

    def get_schema(self, path: str) -> dict[str, str]:
        """Infer schema from first row of data."""
        data = self.read_data(path, limit=1)
        if not data:
            return {}
        return {k: type(v).__name__ for k, v in data[0].items()}
