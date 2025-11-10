try:
    from database_connector import CONNECTION_RETRY, DatabaseConnector
except ImportError:  # pragma: no cover
    from app.database_connector import CONNECTION_RETRY, DatabaseConnector


class SQLiteConnector(DatabaseConnector):
    """Simple connector for SQLite databases."""

    def __init__(self, database_path: str) -> None:
        super().__init__()
        self._database_path = database_path

    @CONNECTION_RETRY
    def _create_connection(self):
        import sqlite3

        connection = sqlite3.connect(
            self._database_path,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES,
            check_same_thread=False,
        )
        return connection

