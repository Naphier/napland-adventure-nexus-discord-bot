from dataclasses import dataclass
from datetime import date, datetime
import calendar
from typing import Any, Dict, Iterable, List, Optional, Tuple

try:
    from database_interface import DatabaseInterface
except ImportError:  # pragma: no cover
    from app.database_interface import DatabaseInterface

try:
    from logger import Logger
except ImportError:  # pragma: no cover
    from app.logger import Logger


@dataclass
class DisplayResult:
    message: str
    ephemeral: bool


class DisplayHandler:
    """Builds DM hour tables for Discord and scheduled EventBridge requests."""

    def __init__(
        self,
        database: DatabaseInterface,
        today_provider=None,
    ) -> None:
        if database is None:
            raise ValueError("database dependency is required")
        self._database = database
        self._today = today_provider or date.today
        self._log = Logger(__file__)

    def handle_discord(self, options: Iterable[Dict[str, Any]]) -> DisplayResult:
        params = self._options_to_dict(options)
        from_date, to_date = self._resolve_dates(params.get("from"), params.get("to"))
        discord_name = params.get("discord_name")
        message = self._render_table(from_date, to_date, discord_name)
        return DisplayResult(message=message, ephemeral=True)

    def handle_event(self, detail: Dict[str, Any]) -> DisplayResult:
        from_value = detail.get("from")
        to_value = detail.get("to")
        discord_name = detail.get("discord_name")
        ephemeral = bool(detail.get("ephemeral", False))
        from_date, to_date = self._resolve_dates(from_value, to_value)
        message = self._render_table(from_date, to_date, discord_name)
        return DisplayResult(message=message, ephemeral=ephemeral)

    def _options_to_dict(self, options: Iterable[Dict[str, Any]]) -> Dict[str, Any]:
        return {option["name"]: option.get("value") for option in options or []}

    def _render_table(
        self,
        from_date: Optional[date],
        to_date: Optional[date],
        discord_name: Optional[str],
    ) -> str:
        self._log.debug(
            f"Fetching records from {from_date} to {to_date} for {discord_name or 'all users'}"
        )
        rows = self._database.fetch_records(from_date, to_date, discord_name)
        range_description = self._describe_range(from_date, to_date)
        if not rows:
            return f"{range_description}\nNo records found for the specified criteria."

        table = self._format_table(rows)
        if discord_name:
            table = f"Filtered for {discord_name}.\n{table}"

        return f"{range_description}\n{table}"

    def _describe_range(self, from_date: Optional[date], to_date: Optional[date]) -> str:
        start = from_date.isoformat() if from_date else "beginning"
        end = to_date.isoformat() if to_date else self._today().isoformat()
        return f"DM Hours from {start} to {end}"

    def _format_table(self, rows: List[Dict[str, Any]]) -> str:
        columns = ["Date", "Discord", "Event", "Hours"]
        table_rows = []
        for row in rows:
            table_rows.append(
                [
                    self._format_date_value(row.get("event_date")),
                    row.get("discord_name", "unknown"),
                    row.get("event_name", "unknown"),
                    self._format_hours(row.get("hours")),
                ]
            )

        widths = [
            max(len(columns[i]), *(len(r[i]) for r in table_rows)) for i in range(len(columns))
        ]
        separator = "+-" + "-+-".join("-" * width for width in widths) + "-+"
        header = "| " + " | ".join(
            columns[i].ljust(widths[i]) for i in range(len(columns))
        ) + " |"
        lines = [separator, header, separator]

        for r in table_rows:
            line = "| " + " | ".join(r[i].ljust(widths[i]) for i in range(len(columns))) + " |"
            lines.append(line)

        lines.append(separator)
        return "\n".join(lines)

    def _format_date_value(self, value: Any) -> str:
        if value is None:
            return "N/A"
        if isinstance(value, date):
            return value.isoformat()
        if isinstance(value, datetime):
            return value.date().isoformat()
        return str(value)

    def _format_hours(self, value: Any) -> str:
        try:
            hours = float(value)
        except (TypeError, ValueError):
            return "0"
        return format(hours, "g")

    def _resolve_dates(
        self, from_value: Optional[str], to_value: Optional[str]
    ) -> Tuple[Optional[date], Optional[date]]:
        today = self._today()
        from_date = self._parse_date(from_value) if from_value else None
        to_date = self._parse_date(to_value) if to_value else None

        if from_date is None and to_date is None:
            return self._previous_month_range(today)

        if to_date is None:
            to_date = today
            return from_date, to_date

        if from_date is None:
            from_date = self._one_month_before(to_date)

        return from_date, to_date

    def _parse_date(self, date_value: str) -> date:
        try:
            return datetime.strptime(date_value, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValueError("dates must use the YYYY-MM-DD format") from exc

    def _one_month_before(self, reference: date) -> date:
        year = reference.year
        month = reference.month - 1
        if month == 0:
            month = 12
            year -= 1
        day = min(reference.day, calendar.monthrange(year, month)[1])
        return date(year, month, day)

    def _previous_month_range(self, today: date) -> Tuple[date, date]:
        first_of_current_month = today.replace(day=1)
        end_year = first_of_current_month.year
        end_month = first_of_current_month.month - 1
        if end_month == 0:
            end_month = 12
            end_year -= 1
        last_day = calendar.monthrange(end_year, end_month)[1]
        start = date(end_year, end_month, 1)
        end = date(end_year, end_month, last_day)
        return start, end
