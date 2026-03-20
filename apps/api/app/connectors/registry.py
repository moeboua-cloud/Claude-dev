"""Connector registry - factory for getting the right connector based on config."""

from app.core.config import get_settings
from app.connectors.base import BaseHRConnector, BaseDirectoryConnector, BaseAppConnector
from app.connectors.mock_workday import MockWorkdayConnector
from app.connectors.mock_ad import MockADConnector
from app.connectors.mock_entra import MockEntraConnector


class ConnectorRegistry:
    """Central registry for all source system connectors."""

    def __init__(self):
        self._settings = get_settings()

    def get_hr_connector(self) -> BaseHRConnector:
        if self._settings.connector_mode == "mock":
            return MockWorkdayConnector()
        # TODO: Production Workday connector
        raise NotImplementedError("Live Workday connector not yet implemented")

    def get_ad_connector(self) -> BaseDirectoryConnector:
        if self._settings.connector_mode == "mock":
            return MockADConnector()
        # TODO: Production AD connector via LDAP
        raise NotImplementedError("Live AD connector not yet implemented")

    def get_entra_connector(self):
        if self._settings.connector_mode == "mock":
            return MockEntraConnector()
        # TODO: Production Entra connector via Microsoft Graph API
        raise NotImplementedError("Live Entra connector not yet implemented")


_registry: ConnectorRegistry | None = None


def get_connector_registry() -> ConnectorRegistry:
    global _registry
    if _registry is None:
        _registry = ConnectorRegistry()
    return _registry
