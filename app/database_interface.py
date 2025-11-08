from typing import Any, Dict, Optional


class DatabaseInterface:
    """Interface describing CRUD helpers for the DM Hours persistence layer."""

    def create_record(self, data: Dict[str, Any]) -> None:
        """Persist a new record in the backing store."""
        # Stub method to be implemented by concrete database helpers.
        return None

    def read_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        """Fetch a record by its identifier."""
        return None

    def update_record(self, record_id: str, data: Dict[str, Any]) -> None:
        """Update an existing record."""
        return None

    def delete_record(self, record_id: str) -> None:
        """Remove a record from the backing store."""
        return None

    def fetch_records(self, start_date=None, end_date=None, discord_name: Optional[str] = None):
        """Return iterable records constrained by optional filters."""
        return []
