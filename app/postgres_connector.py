try:
    from database_connector import CONNECTION_RETRY, DatabaseConnector
except ImportError:  # pragma: no cover
    from app.database_connector import CONNECTION_RETRY, DatabaseConnector


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

    @CONNECTION_RETRY
    def _create_connection(self):
        try:
            import psycopg2
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise RuntimeError(
                "psycopg2 is required for Postgres connections but is not installed"
            ) from exc

        connection = psycopg2.connect(**self._config)
        connection.autocommit = False
        return connection

