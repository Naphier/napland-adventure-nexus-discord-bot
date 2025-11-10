from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Optional

from tenacity import retry, stop_after_attempt, wait_fixed


CONNECTION_RETRY = retry(
    stop=stop_after_attempt(3),
    wait=wait_fixed(1),
    reraise=True,
)


class DatabaseConnector(ABC):
    """Base connector that lazily creates and caches DB-API connections."""

    def __init__(self) -> None:
        self._connection: Optional[Any] = None
        self._lock = Lock()

    def get_connection(self):
        if self._connection is None:
            with self._lock:
                if self._connection is None:
                    self._connection = self._create_connection()
        return self._connection

    def close_connection(self) -> None:
        with self._lock:
            if self._connection is not None:
                self._close(self._connection)
                self._connection = None

    @abstractmethod
    def _create_connection(self):
        """Instantiate a DB-API compatible connection."""

    def _close(self, connection) -> None:
        connection.close()


__all__ = ["DatabaseConnector", "CONNECTION_RETRY"]
