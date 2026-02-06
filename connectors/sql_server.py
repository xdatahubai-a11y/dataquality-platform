"""SQL Server data source connector."""

from typing import Optional

from connectors.base import DataConnector


class SQLServerConnector(DataConnector):
    """Connector for Microsoft SQL Server via pyodbc."""

    def __init__(self) -> None:
        self._connection = None
        self._connection_string: str = ""

    def connect(self, config: dict) -> None:
        """Connect to SQL Server.

        Config keys: server, database, username, password, driver (optional).
        Or: connection_string for full ODBC connection string.
        """
        try:
            import pyodbc
        except ImportError:
            raise RuntimeError("pyodbc package required")

        if "connection_string" in config:
            self._connection_string = config["connection_string"]
        else:
            driver = config.get("driver", "ODBC Driver 18 for SQL Server")
            self._connection_string = (
                f"DRIVER={{{driver}}};"
                f"SERVER={config['server']};"
                f"DATABASE={config['database']};"
                f"UID={config.get('username', '')};"
                f"PWD={config.get('password', '')};"
                f"TrustServerCertificate=yes;"
            )

        self._connection = pyodbc.connect(self._connection_string)

    def test_connection(self) -> bool:
        """Test SQL Server connection."""
        if not self._connection:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.close()
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from a SQL Server table or query.

        Args:
            path: Table name or SQL query (prefixed with 'sql:').
        """
        if not self._connection:
            raise RuntimeError("Not connected. Call connect() first.")

        cursor = self._connection.cursor()

        if path.startswith("sql:"):
            query = path[4:]
        else:
            cols = ", ".join(columns) if columns else "*"
            query = f"SELECT {cols} FROM {path}"
            if limit:
                query = f"SELECT TOP {limit} {cols} FROM {path}"

        cursor.execute(query)
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        return [{col_names[i]: row[i] for i in range(len(col_names))} for row in rows]

    def list_tables(self) -> list[str]:
        """List tables in the connected database."""
        if not self._connection:
            return []
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT TABLE_SCHEMA + '.' + TABLE_NAME FROM INFORMATION_SCHEMA.TABLES "
            "WHERE TABLE_TYPE = 'BASE TABLE'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def get_schema(self, path: str) -> dict[str, str]:
        """Get table schema from SQL Server."""
        if not self._connection:
            return {}
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT COLUMN_NAME, DATA_TYPE FROM INFORMATION_SCHEMA.COLUMNS "
            f"WHERE TABLE_NAME = '{path}'"
        )
        schema = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        return schema
