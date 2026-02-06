"""Tests for data source connectors (mocked)."""

import pytest
from unittest.mock import MagicMock, patch

from connectors.base import DataConnector
from connectors.adls_gen2 import ADLSGen2Connector
from connectors.sql_server import SQLServerConnector


class TestDataConnectorInterface:
    """Test that connectors implement the interface."""

    def test_adls_gen2_is_connector(self):
        assert issubclass(ADLSGen2Connector, DataConnector)

    def test_sql_server_is_connector(self):
        assert issubclass(SQLServerConnector, DataConnector)

    def test_adls_not_connected(self):
        connector = ADLSGen2Connector()
        assert connector.test_connection() is False

    def test_sql_not_connected(self):
        connector = SQLServerConnector()
        assert connector.test_connection() is False


class TestADLSGen2Connector:
    def test_connect_without_azure_sdk(self):
        """Test ADLS connector stores config on connect attempt."""
        connector = ADLSGen2Connector()
        try:
            connector.connect({"account_name": "test", "account_key": "key123", "container": "data"})
        except RuntimeError:
            pass  # Expected if azure SDK not installed
        assert connector._account_name == "test"

    def test_read_not_connected(self):
        connector = ADLSGen2Connector()
        with pytest.raises(RuntimeError, match="Not connected"):
            connector.read_data("test.json")

    def test_list_tables_not_connected(self):
        connector = ADLSGen2Connector()
        assert connector.list_tables() == []
