try:
    from database_connector import CONNECTION_RETRY, DatabaseConnector
except ImportError:  # pragma: no cover
    from app.database_connector import CONNECTION_RETRY, DatabaseConnector


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

    @CONNECTION_RETRY
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

