import unittest
from datetime import date

from app.database_interface import DatabaseInterface
from app.log_hours_handler import LogHoursHandler


class FakeDatabase(DatabaseInterface):
    def __init__(self):
        self.created_records = []

    def create_record(self, data):
        self.created_records.append(data)


class LogHoursHandlerTestCase(unittest.TestCase):
    def setUp(self):
        self.database = FakeDatabase()
        self.handler = LogHoursHandler(self.database)
        self.user_id = "user-123"

    def test_handle_persists_record_and_returns_confirmation(self):
        options = [
            {"name": "event", "value": "Weekly Raid"},
            {"name": "hours", "value": 2.5},
            {"name": "date", "value": "2024-06-01"},
        ]

        message = self.handler.handle(options, self.user_id)

        self.assertEqual(
            message,
            "Logged 2.5 hours for 'Weekly Raid' on 2024-06-01.",
        )
        self.assertEqual(len(self.database.created_records), 1)
        record = self.database.created_records[0]
        self.assertEqual(record["user_id"], self.user_id)
        self.assertEqual(record["event_name"], "Weekly Raid")
        self.assertEqual(record["hours"], 2.5)
        self.assertEqual(record["event_date"], date(2024, 6, 1))

    def test_handle_rejects_invalid_date_format(self):
        options = [
            {"name": "event", "value": "Weekly Raid"},
            {"name": "hours", "value": 2},
            {"name": "date", "value": "06-01-2024"},
        ]

        with self.assertRaisesRegex(ValueError, "YYYY-MM-DD"):
            self.handler.handle(options, self.user_id)

    def test_handle_rejects_non_positive_hours(self):
        options = [
            {"name": "event", "value": "Weekly Raid"},
            {"name": "hours", "value": 0},
            {"name": "date", "value": "2024-06-01"},
        ]

        with self.assertRaisesRegex(ValueError, "greater than zero"):
            self.handler.handle(options, self.user_id)

    def test_handle_rejects_empty_event_name(self):
        options = [
            {"name": "event", "value": "   "},
            {"name": "hours", "value": 2},
            {"name": "date", "value": "2024-06-01"},
        ]

        with self.assertRaisesRegex(ValueError, "event name cannot be empty"):
            self.handler.handle(options, self.user_id)

    def test_handle_detects_missing_option(self):
        options = [
            {"name": "event", "value": "Weekly Raid"},
            {"name": "hours", "value": 2},
        ]

        with self.assertRaisesRegex(ValueError, "Missing required option"):
            self.handler.handle(options, self.user_id)


if __name__ == "__main__":
    unittest.main()
