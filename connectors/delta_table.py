"""Delta Lake table connector."""

from typing import Optional

from connectors.base import DataConnector


class DeltaTableConnector(DataConnector):
    """Connector for Delta Lake tables via PySpark."""

    def __init__(self) -> None:
        self._spark = None
        self._path: str = ""

    def connect(self, config: dict) -> None:
        """Connect by creating a SparkSession with Delta support.

        Config keys: spark_master (default: local[*]), delta_path.
        """
        try:
            from pyspark.sql import SparkSession

            master = config.get("spark_master", "local[*]")
            self._path = config.get("delta_path", "")

            self._spark = (
                SparkSession.builder.master(master)
                .appName("DQ-DeltaConnector")
                .config("spark.jars.packages", "io.delta:delta-spark_2.12:3.0.0")
                .config("spark.sql.extensions", "io.delta.sql.DeltaSparkSessionExtension")
                .config(
                    "spark.sql.catalog.spark_catalog",
                    "org.apache.spark.sql.delta.catalog.DeltaCatalog",
                )
                .getOrCreate()
            )
        except ImportError:
            raise RuntimeError("pyspark and delta-spark packages required")

    def test_connection(self) -> bool:
        """Test Delta connection by reading metadata."""
        if not self._spark:
            return False
        try:
            self._spark.read.format("delta").load(self._path).limit(0)
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from a Delta table."""
        if not self._spark:
            raise RuntimeError("Not connected. Call connect() first.")

        df = self._spark.read.format("delta").load(path or self._path)
        if columns:
            df = df.select(*columns)
        if limit:
            df = df.limit(limit)
        return [row.asDict() for row in df.collect()]

    def list_tables(self) -> list[str]:
        """List available Delta tables (catalog-based)."""
        if not self._spark:
            return []
        try:
            tables = self._spark.catalog.listTables()
            return [t.name for t in tables]
        except Exception:
            return []

    def get_schema(self, path: str) -> dict[str, str]:
        """Get Delta table schema."""
        if not self._spark:
            return {}
        df = self._spark.read.format("delta").load(path or self._path)
        return {f.name: str(f.dataType) for f in df.schema.fields}
