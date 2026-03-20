"""Base connector interface for all source system adapters."""

from abc import ABC, abstractmethod
from typing import Any


class BaseConnector(ABC):
    """Read-only connector interface for source systems."""

    @abstractmethod
    async def test_connection(self) -> bool:
        """Verify connectivity to the source system."""
        ...

    @abstractmethod
    async def fetch_users(self) -> list[dict[str, Any]]:
        """Fetch all user records from the source system."""
        ...

    @abstractmethod
    async def fetch_user(self, identifier: str) -> dict[str, Any] | None:
        """Fetch a single user by identifier."""
        ...

    @abstractmethod
    async def fetch_groups(self) -> list[dict[str, Any]]:
        """Fetch group/role data from the source system."""
        ...

    @abstractmethod
    async def fetch_group_members(self, group_id: str) -> list[str]:
        """Fetch member identifiers for a group."""
        ...


class BaseHRConnector(BaseConnector):
    """HR-specific connector with worker lifecycle data."""

    @abstractmethod
    async def fetch_worker_lifecycle(self, employee_id: str) -> list[dict[str, Any]]:
        """Fetch lifecycle events for a worker."""
        ...

    @abstractmethod
    async def fetch_org_structure(self) -> list[dict[str, Any]]:
        """Fetch org hierarchy data."""
        ...


class BaseDirectoryConnector(BaseConnector):
    """Directory service connector (AD / Entra)."""

    @abstractmethod
    async def fetch_user_memberships(self, user_id: str) -> list[dict[str, Any]]:
        """Fetch group memberships for a user."""
        ...


class BaseAppConnector(ABC):
    """Application-specific connector for entitlements."""

    @abstractmethod
    async def fetch_app_roles(self) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def fetch_user_assignments(self, app_id: str) -> list[dict[str, Any]]:
        ...

    @abstractmethod
    async def fetch_user_app_access(self, user_id: str) -> list[dict[str, Any]]:
        ...
