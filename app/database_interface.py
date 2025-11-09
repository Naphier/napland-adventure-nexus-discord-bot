from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

try:
    from database_connector import DatabaseConnector
except ImportError:  # pragma: no cover
    from app.database_connector import DatabaseConnector


class DatabaseInterface(ABC):
    """Interface describing CRUD helpers for the DM Hours persistence layer."""

    def __init__(self, connector: DatabaseConnector) -> None:
        if connector is None:
            raise ValueError("Database connector is required")
        self._connector = connector

    @abstractmethod
    def create_record(self, data: Dict[str, Any]) -> None:
        """Persist a new record in the backing store."""

    @abstractmethod
    def read_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a record by its identifier."""

    @abstractmethod
    def update_record(self, record_id: str, data: Dict[str, Any]) -> None:
        """Update an existing record."""

    @abstractmethod
    def delete_record(self, record_id: str) -> None:
        """Remove a record from the backing store."""

    @abstractmethod
    def fetch_records(
        self,
        start_date=None,
        end_date=None,
        discord_name: Optional[str] = None,
    ):
        """Return iterable records constrained by optional filters."""
