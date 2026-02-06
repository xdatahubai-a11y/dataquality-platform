"""PostgreSQL data source connector."""

from typing import Optional

from connectors.base import DataConnector


class PostgreSQLConnector(DataConnector):
    """Connector for PostgreSQL via psycopg2."""

    def __init__(self) -> None:
        self._connection = None
        self._schema: str = "public"

    def connect(self, config: dict) -> None:
        """Connect to PostgreSQL.

        Config keys: host, port, database, username, password, schema, sslmode.
        Or: connection_string for full DSN.
        """
        try:
            import psycopg2
        except ImportError:
            raise RuntimeError("psycopg2-binary package required")

        self._schema = config.get("schema", "public")

        if "connection_string" in config:
            self._connection = psycopg2.connect(config["connection_string"])
        else:
            self._connection = psycopg2.connect(
                host=config.get("host", "localhost"),
                port=config.get("port", 5432),
                dbname=config["database"],
                user=config.get("username", ""),
                password=config.get("password", ""),
                sslmode=config.get("sslmode", "prefer"),
            )

    def test_connection(self) -> bool:
        """Test PostgreSQL connection."""
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
        """Read data from a PostgreSQL table or query.

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
            query = f"SELECT {cols} FROM {self._schema}.{path}"
            if limit:
                query += f" LIMIT {limit}"

        cursor.execute(query)
        col_names = [desc[0] for desc in cursor.description]
        rows = cursor.fetchall()
        cursor.close()

        return [{col_names[i]: row[i] for i in range(len(col_names))} for row in rows]

    def list_tables(self) -> list[str]:
        """List tables in the connected database schema."""
        if not self._connection:
            return []
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT table_schema || '.' || table_name FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = 'BASE TABLE'",
            (self._schema,),
        )
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def get_schema(self, path: str) -> dict[str, str]:
        """Get table schema from PostgreSQL."""
        if not self._connection:
            return {}
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = %s AND table_schema = %s",
            (path, self._schema),
        )
        schema = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        return schema
