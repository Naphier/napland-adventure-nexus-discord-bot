from datetime import date, datetime
from typing import Any, Dict, Iterable

try:
    from database_interface import DatabaseInterface
except ImportError:  # pragma: no cover
    from app.database_interface import DatabaseInterface


class LogHoursHandler:
    """Parses hour logging commands and persists them via the database layer."""

    REQUIRED_FIELDS = ("date", "hours", "event")

    def __init__(self, database: DatabaseInterface) -> None:
        if database is None:
            raise ValueError("database dependency is required")
        self._database = database

    def handle(self, options: Iterable[Dict[str, Any]], user_id: str) -> str:
        """Validate incoming options, persist them, and craft a confirmation message."""
        normalized_options = self._options_to_dict(options)
        self._assert_required_fields(normalized_options)

        event_date = self._parse_date(normalized_options["date"])
        hours = self._parse_hours(normalized_options["hours"])
        event_name = self._parse_event_name(normalized_options["event"])

        record = {
            "user_id": user_id,
            "event_date": event_date,
            "hours": hours,
            "event_name": event_name,
        }

        self._database.create_record(record)

        human_hours = self._format_hours(hours)
        return f"Logged {human_hours} hours for '{event_name}' on {event_date.isoformat()}."

    def _options_to_dict(self, options: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        return {option["name"]: option.get("value") for option in options}

    def _assert_required_fields(self, options: Dict[str, Any]) -> None:
        missing = [field for field in self.REQUIRED_FIELDS if field not in options]
        if missing:
            raise ValueError(f"Missing required option(s): {', '.join(missing)}")

    def _parse_date(self, date_value: Any) -> date:
        if not isinstance(date_value, str):
            raise ValueError("date must be provided as a YYYY-MM-DD string")
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("date must follow the YYYY-MM-DD format") from exc

    def _parse_hours(self, hours_value: Any) -> float:
        try:
            hours_float = float(hours_value)
        except (TypeError, ValueError) as exc:
            raise ValueError("hours must be a numeric value") from exc

        if hours_float <= 0:
            raise ValueError("hours must be greater than zero")
        return hours_float

    def _parse_event_name(self, event_value: Any) -> str:
        if not isinstance(event_value, str):
            raise ValueError("event name must be a string")
        event_name = event_value.strip()
        if not event_name:
            raise ValueError("event name cannot be empty")
        return event_name

    def _format_hours(self, hours: float) -> str:
        # Use general format to avoid trailing zeros for whole numbers.
        return format(hours, "g")
