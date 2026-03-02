"""Data source connectors."""

from connectors.adls_gen2 import ADLSGen2Connector
from connectors.base import DataConnector
from connectors.bigquery import BigQueryConnector
from connectors.delta_table import DeltaTableConnector
from connectors.glue_catalog import GlueCatalogConnector
from connectors.mysql import MySQLConnector
from connectors.postgresql import PostgreSQLConnector
from connectors.redshift import RedshiftConnector
from connectors.s3 import S3Connector
from connectors.sql_server import SQLServerConnector
from connectors.sqlite import SQLiteConnector

__all__ = [
    "DataConnector",
    "ADLSGen2Connector",
    "BigQueryConnector",
    "DeltaTableConnector",
    "GlueCatalogConnector",
    "MySQLConnector",
    "PostgreSQLConnector",
    "RedshiftConnector",
    "S3Connector",
    "SQLServerConnector",
    "SQLiteConnector",
]


def get_connector(source_type: str) -> type[DataConnector]:
    """Factory function to get the appropriate connector class by type."""
    connector_map = {
        "adls_gen2": ADLSGen2Connector,
        "bigquery": BigQueryConnector,
        "delta_table": DeltaTableConnector,
        "glue_catalog": GlueCatalogConnector,
        "mysql": MySQLConnector,
        "postgresql": PostgreSQLConnector,
        "redshift": RedshiftConnector,
        "s3": S3Connector,
        "sql_server": SQLServerConnector,
        "sqlite": SQLiteConnector,
    }

    if source_type not in connector_map:
        raise ValueError(f"Unsupported source type: {source_type}")

    return connector_map[source_type]
