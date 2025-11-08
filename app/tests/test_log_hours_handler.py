from datetime import date

import pytest

from app.database_interface import DatabaseInterface
from app.log_hours_handler import LogHoursHandler


class FakeDatabase(DatabaseInterface):
    def __init__(self):
        self.created_records = []

    def create_record(self, data):
        self.created_records.append(data)


@pytest.fixture
def database():
    return FakeDatabase()


@pytest.fixture
def handler(database):
    return LogHoursHandler(database)


@pytest.fixture
def user_id():
    return "user-123"


def test_handle_persists_record_and_returns_confirmation(handler, database, user_id):
    options = [
        {"name": "event", "value": "Weekly Raid"},
        {"name": "hours", "value": 2.5},
        {"name": "date", "value": "2024-06-01"},
    ]

    message = handler.handle(options, user_id)

    assert message == "Logged 2.5 hours for 'Weekly Raid' on 2024-06-01."
    assert len(database.created_records) == 1
    record = database.created_records[0]
    assert record["user_id"] == user_id
    assert record["event_name"] == "Weekly Raid"
    assert record["hours"] == 2.5
    assert record["event_date"] == date(2024, 6, 1)


def test_handle_rejects_invalid_date_format(handler, user_id):
    options = [
        {"name": "event", "value": "Weekly Raid"},
        {"name": "hours", "value": 2},
        {"name": "date", "value": "06-01-2024"},
    ]

    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        handler.handle(options, user_id)


def test_handle_rejects_non_positive_hours(handler, user_id):
    options = [
        {"name": "event", "value": "Weekly Raid"},
        {"name": "hours", "value": 0},
        {"name": "date", "value": "2024-06-01"},
    ]

    with pytest.raises(ValueError, match="greater than zero"):
        handler.handle(options, user_id)


def test_handle_rejects_empty_event_name(handler, user_id):
    options = [
        {"name": "event", "value": "   "},
        {"name": "hours", "value": 2},
        {"name": "date", "value": "2024-06-01"},
    ]

    with pytest.raises(ValueError, match="event name cannot be empty"):
        handler.handle(options, user_id)


def test_handle_detects_missing_option(handler, user_id):
    options = [
        {"name": "event", "value": "Weekly Raid"},
        {"name": "hours", "value": 2},
    ]

    with pytest.raises(ValueError, match="Missing required option"):
        handler.handle(options, user_id)
