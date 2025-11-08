import unittest
from datetime import date

from app.database_interface import DatabaseInterface
from app.display_handler import DisplayHandler


class FakeDatabase(DatabaseInterface):
    def __init__(self):
        self.records = []
        self.last_query = None

    def fetch_records(self, start_date=None, end_date=None, discord_name=None):
        self.last_query = (start_date, end_date, discord_name)
        return self.records


class DisplayHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.database = FakeDatabase()
        self.today = lambda: date(2025, 11, 8)
        self.handler = DisplayHandler(self.database, today_provider=self.today)

    def test_handle_discord_renders_table_and_is_ephemeral(self):
        self.database.records = [
            {
                "event_date": date(2025, 10, 2),
                "discord_name": "Hero",
                "event_name": "Session Zero",
                "hours": 3.5,
            }
        ]
        options = [
            {"name": "from", "value": "2025-10-01"},
            {"name": "to", "value": "2025-10-31"},
        ]

        result = self.handler.handle_discord(options)

        self.assertTrue(result.ephemeral)
        self.assertIn("DM Hours from 2025-10-01 to 2025-10-31", result.message)
        self.assertIn("Hero", result.message)
        self.assertEqual(
            self.database.last_query,
            (date(2025, 10, 1), date(2025, 10, 31), None),
        )

    def test_handle_discord_without_from_uses_prior_month_window(self):
        self.database.records = []
        options = [{"name": "to", "value": "2025-08-15"}]

        result = self.handler.handle_discord(options)

        expected_start = date(2025, 7, 15)
        self.assertEqual(
            self.database.last_query,
            (expected_start, date(2025, 8, 15), None),
        )
        self.assertIn("No records found", result.message)

    def test_handle_discord_without_any_dates_defaults_to_previous_month(self):
        self.database.records = []
        result = self.handler.handle_discord([])

        # Previous month relative to Nov 8, 2025 is Oct 1 - Oct 31, 2025
        self.assertEqual(
            self.database.last_query,
            (date(2025, 10, 1), date(2025, 10, 31), None),
        )
        self.assertIn("2025-10-01", result.message)

    def test_handle_event_allows_ephemeral_override(self):
        self.database.records = []
        detail = {
            "from": "2025-09-01",
            "to": "2025-09-30",
            "discord_name": "Hero",
            "ephemeral": True,
        }

        result = self.handler.handle_event(detail)

        self.assertTrue(result.ephemeral)
        self.assertEqual(
            self.database.last_query,
            (date(2025, 9, 1), date(2025, 9, 30), "Hero"),
        )

    def test_handle_event_without_to_uses_today(self):
        self.database.records = []
        detail = {"from": "2025-01-01"}

        self.handler.handle_event(detail)

        self.assertEqual(
            self.database.last_query,
            (date(2025, 1, 1), self.today(), None),
        )


if __name__ == "__main__":
    unittest.main()

