"""Abstract base class for data source connectors."""

from abc import ABC, abstractmethod
from typing import Any, Optional


class DataConnector(ABC):
    """Abstract interface for all data source connectors."""

    @abstractmethod
    def connect(self, config: dict) -> None:
        """Establish connection to the data source."""
        ...

    @abstractmethod
    def test_connection(self) -> bool:
        """Test if the connection is valid."""
        ...

    @abstractmethod
    def read_data(
        self, path: str, limit: Optional[int] = None, columns: Optional[list[str]] = None
    ) -> list[dict]:
        """Read data from the source and return as list of dicts.

        Args:
            path: Table name, file path, or query.
            limit: Max rows to return.
            columns: Specific columns to select.

        Returns:
            List of row dictionaries.
        """
        ...

    @abstractmethod
    def list_tables(self) -> list[str]:
        """List available tables or paths in the source."""
        ...

    @abstractmethod
    def get_schema(self, path: str) -> dict[str, str]:
        """Get schema (column name -> type) for a table/path."""
        ...
