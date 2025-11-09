from datetime import date, datetime
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple
from tenacity import retry, stop_after_attempt, wait_fixed


try:
    from database_interface import DatabaseInterface
except ImportError:  # pragma: no cover
    from app.database_interface import DatabaseInterface


class DatabaseHandlerSQL(DatabaseInterface):
    """Database handler that performs parameterized SQL operations with retry support."""

    ALLOWED_FIELDS = (
        "user_id",
        "discord_name",
        "event_name",
        "event_date",
        "hours",
    )
    SELECT_FIELDS = ("id",) + ALLOWED_FIELDS

    def __init__(self, connector, table_name: str = "dm_hours") -> None:
        super().__init__(connector)
        self._table_name = table_name

    def create_record(self, data: Dict[str, Any]) -> None:
        fields, values = self._sanitize_payload(data)
        if not fields:
            raise ValueError("No valid fields provided for insert")
        placeholders = ", ".join(["?"] * len(values))
        columns = ", ".join(fields)
        query = f"INSERT INTO {self._table_name} ({columns}) VALUES ({placeholders})"
        self._execute(query, values, commit=True)

    def read_record(self, record_id: str) -> Optional[Dict[str, Any]]:
        query = self._base_select() + " WHERE id = ?"
        rows = self._execute(query, (record_id,), fetch_all=True)
        return rows[0] if rows else None

    def update_record(self, record_id: str, data: Dict[str, Any]) -> None:
        fields, values = self._sanitize_payload(data)
        if not fields:
            raise ValueError("No valid fields provided for update")
        set_clause = ", ".join(f"{field} = ?" for field in fields)
        query = f"UPDATE {self._table_name} SET {set_clause} WHERE id = ?"
        self._execute(query, tuple(values) + (record_id,), commit=True)

    def delete_record(self, record_id: str) -> None:
        query = f"DELETE FROM {self._table_name} WHERE id = ?"
        self._execute(query, (record_id,), commit=True)

    def fetch_records(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        discord_name: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        query = self._base_select() + " WHERE 1=1"
        params: List[Any] = []
        if start_date:
            query += " AND event_date >= ?"
            params.append(self._coerce_date(start_date))
        if end_date:
            query += " AND event_date <= ?"
            params.append(self._coerce_date(end_date))
        if discord_name:
            query += " AND discord_name = ?"
            params.append(discord_name)
        query += " ORDER BY event_date DESC"
        return self._execute(query, tuple(params), fetch_all=True)

    def _base_select(self) -> str:
        columns = ", ".join(self.SELECT_FIELDS)
        return f"SELECT {columns} FROM {self._table_name}"

    def _sanitize_payload(self, data: Dict[str, Any]) -> Tuple[Tuple[str, ...], Tuple[Any, ...]]:
        filtered: List[Tuple[str, Any]] = []
        for field in self.ALLOWED_FIELDS:
            if field in data and data[field] is not None:
                value = data[field]
                if field == "event_date":
                    value = self._coerce_date(value)
                filtered.append((field, value))
        fields = tuple(field for field, _ in filtered)
        values = tuple(value for _, value in filtered)
        return fields, values

    def _coerce_date(self, value: Any) -> str:
        if isinstance(value, datetime):
            return value.date().isoformat()
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, str):
            return value
        raise ValueError("event_date must be a date, datetime, or ISO string")

    def _execute(
        self,
        query: str,
        params: Sequence[Any] = (),
        *,
        fetch_all: bool = False,
        commit: bool = False,
    ):
        return self._execute_with_retry(query, params, fetch_all, commit)

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(0), reraise=True)
    def _execute_with_retry(
        self,
        query: str,
        params: Sequence[Any],
        fetch_all: bool,
        commit: bool,
    ):
        connection = self._connector.get_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(query, params)
            result = None
            if fetch_all:
                rows = cursor.fetchall()
                result = self._rows_to_dict(cursor.description, rows)
            if commit:
                connection.commit()
            return result if fetch_all else None
        finally:
            cursor.close()

    def _rows_to_dict(
        self,
        description: Iterable[Tuple],
        rows: Iterable[Tuple[Any, ...]],
    ) -> List[Dict[str, Any]]:
        columns = [col[0] for col in description]
        formatted_rows = []
        for row in rows:
            record = dict(zip(columns, row))
            formatted_rows.append(record)
        return formatted_rows
