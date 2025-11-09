import unittest
from unittest import mock
from datetime import date

from app.database_connector import DatabaseConnector
from app.database_handler_sql import DatabaseHandlerSQL


class MockConnector(DatabaseConnector):
    def __init__(self, connection):
        super().__init__()
        self._provided_connection = connection

    def _create_connection(self):
        return self._provided_connection


class DatabaseHandlerSQLTestCase(unittest.TestCase):
    def setUp(self):
        self.connection = mock.MagicMock()
        self.cursor = mock.MagicMock()
        self.connection.cursor.return_value = self.cursor
        self.connector = MockConnector(self.connection)
        self.handler = DatabaseHandlerSQL(self.connector, table_name="dm_hours")

    def test_create_record_uses_parameterized_query(self):
        data = {
            "user_id": "123",
            "discord_name": "Hero",
            "event_name": "Session",
            "event_date": date(2024, 6, 1),
            "hours": 4.0,
        }

        self.handler.create_record(data)

        self.cursor.execute.assert_called_once_with(
            "INSERT INTO dm_hours (user_id, discord_name, event_name, event_date, hours) VALUES (?, ?, ?, ?, ?)",
            ("123", "Hero", "Session", "2024-06-01", 4.0),
        )
        self.connection.commit.assert_called_once()

    def test_fetch_records_returns_dicts(self):
        self.cursor.description = [
            ("id", None, None, None, None, None, None),
            ("user_id", None, None, None, None, None, None),
            ("discord_name", None, None, None, None, None, None),
            ("event_name", None, None, None, None, None, None),
            ("event_date", None, None, None, None, None, None),
            ("hours", None, None, None, None, None, None),
        ]
        self.cursor.fetchall.return_value = [
            (1, "123", "Hero", "Session", "2024-06-01", 3.5),
        ]

        rows = self.handler.fetch_records(
            start_date=date(2024, 6, 1),
            end_date=date(2024, 6, 30),
            discord_name="Hero",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["discord_name"], "Hero")
        self.assertIn("AND event_date >= ?", self.cursor.execute.call_args[0][0])
        self.assertIn("AND event_date <= ?", self.cursor.execute.call_args[0][0])
        self.assertIn("AND discord_name = ?", self.cursor.execute.call_args[0][0])

    def test_update_record_without_fields_raises(self):
        with self.assertRaises(ValueError):
            self.handler.update_record("123", {"unknown": "value"})
        with self.assertRaises(ValueError):
            self.handler.create_record({})

    def test_delete_record_commits(self):
        self.handler.delete_record("123")
        self.cursor.execute.assert_called_once_with(
            "DELETE FROM dm_hours WHERE id = ?", ("123",)
        )
        self.connection.commit.assert_called_once()

    def test_retry_on_transient_error(self):
        self.cursor.execute.side_effect = [
            RuntimeError("temporary"),
            None,
        ]
        self.cursor.fetchall.return_value = []
        self.cursor.description = []

        self.handler.fetch_records()

        self.assertEqual(self.cursor.execute.call_count, 2)


if __name__ == "__main__":
    unittest.main()
