"""MySQL data source connector."""

from typing import Optional

from connectors.base import DataConnector


class MySQLConnector(DataConnector):
    """Connector for MySQL via mysql-connector-python."""

    def __init__(self) -> None:
        self._connection = None
        self._database: str = ""

    def connect(self, config: dict) -> None:
        """Connect to MySQL.

        Config keys: host, port, database, username, password, charset, ssl_ca, ssl_cert, ssl_key.
        """
        try:
            import mysql.connector
        except ImportError:
            raise RuntimeError("mysql-connector-python package required")

        self._database = config.get("database", "")

        connect_args: dict = {
            "host": config.get("host", "localhost"),
            "port": config.get("port", 3306),
            "database": config["database"],
            "user": config.get("username", ""),
            "password": config.get("password", ""),
            "charset": config.get("charset", "utf8mb4"),
        }

        # SSL support
        ssl_config: dict = {}
        if config.get("ssl_ca"):
            ssl_config["ca"] = config["ssl_ca"]
        if config.get("ssl_cert"):
            ssl_config["cert"] = config["ssl_cert"]
        if config.get("ssl_key"):
            ssl_config["key"] = config["ssl_key"]
        if ssl_config:
            connect_args["ssl_ca"] = ssl_config.get("ca")

        self._connection = mysql.connector.connect(**connect_args)

    def test_connection(self) -> bool:
        """Test MySQL connection."""
        if not self._connection:
            return False
        try:
            cursor = self._connection.cursor()
            cursor.execute("SELECT 1")
            cursor.fetchall()
            cursor.close()
            return True
        except Exception:
            return False

    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from a MySQL table or query.

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
                query += f" LIMIT {limit}"

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
            "SELECT table_name FROM information_schema.tables "
            "WHERE table_schema = %s AND table_type = 'BASE TABLE'",
            (self._database,),
        )
        tables = [row[0] for row in cursor.fetchall()]
        cursor.close()
        return tables

    def get_schema(self, path: str) -> dict[str, str]:
        """Get table schema from MySQL."""
        if not self._connection:
            return {}
        cursor = self._connection.cursor()
        cursor.execute(
            "SELECT column_name, data_type FROM information_schema.columns "
            "WHERE table_name = %s AND table_schema = %s",
            (path, self._database),
        )
        schema = {row[0]: row[1] for row in cursor.fetchall()}
        cursor.close()
        return schema
