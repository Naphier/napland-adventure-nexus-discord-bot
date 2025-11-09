from abc import ABC, abstractmethod
from threading import Lock
from typing import Any, Optional
from tenacity import retry, stop_after_attempt, wait_fixed

_CONNECTION_RETRY = retry(stop=stop_after_attempt(3), wait=wait_fixed(1), reraise=True)


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


class SQLiteConnector(DatabaseConnector):
    """Simple connector for SQLite databases."""

    def __init__(self, database_path: str) -> None:
        super().__init__()
        self._database_path = database_path

    @_CONNECTION_RETRY
    def _create_connection(self):
        import sqlite3

        connection = sqlite3.connect(
            self._database_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        return connection


class PostgresConnector(DatabaseConnector):
    """Connector for PostgreSQL databases using psycopg2."""

    def __init__(
        self,
        *,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 5432,
        sslmode: str | None = None,
        connect_timeout: int = 10,
    ) -> None:
        super().__init__()
        self._config = {
            "host": host,
            "port": port,
            "dbname": database,
            "user": user,
            "password": password,
            "connect_timeout": connect_timeout,
        }
        if sslmode:
            self._config["sslmode"] = sslmode

    @_CONNECTION_RETRY
    def _create_connection(self):
        try:
            import psycopg2
        except ImportError as exc:  # pragma: no cover - depends on optional dependency
            raise RuntimeError(
                "psycopg2 is required for Postgres connections but is not installed"
            ) from exc

        connection = psycopg2.connect(**self._config)
        connection.autocommit = False
        return connection


class MySQLConnector(DatabaseConnector):
    """Connector for MySQL-compatible databases using mysql-connector-python."""

    def __init__(
        self,
        *,
        host: str,
        database: str,
        user: str,
        password: str,
        port: int = 3306,
        ssl_ca: str | None = None,
        connect_timeout: int = 10,
    ) -> None:
        super().__init__()
        self._config = {
            "host": host,
            "port": port,
            "database": database,
            "user": user,
            "password": password,
            "connection_timeout": connect_timeout,
        }
        if ssl_ca:
            self._config["ssl_ca"] = ssl_ca

    @_CONNECTION_RETRY
    def _create_connection(self):
        try:
            import mysql.connector
        except ImportError as exc:  # pragma: no cover
            raise RuntimeError(
                "mysql-connector-python is required for MySQL connections but is not installed"
            ) from exc

        connection = mysql.connector.connect(**self._config)
        connection.autocommit = False
        return connection
