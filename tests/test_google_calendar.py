import pytest
import os
from unittest.mock import Mock, patch, MagicMock
from google_calendar import Calendar, collect_events
import datetime
import time
import dateutil.tz
from oauth2client.service_account import ServiceAccountCredentials


# Mock the API calls to return a fixed event list
sample_event = {
    'summary': 'Test Event',
    'start': {'dateTime': '2023-08-16T10:00:00+00:00'},
    'end': {'dateTime': '2023-08-16T11:00:00+00:00'}
}


@pytest.fixture
def mock_google_calendar():
    with patch('google_calendar.Calendar.get_last_events', return_value=[sample_event]) as mock_get:
        yield mock_get


def test_parse_time():
    calendar = Calendar({'credentials_file_name': 'path_to_credentials.json'}, 'some_id')
    parsed_time = calendar.parse_time('2023-08-16T10:00:00+00:00')
    assert parsed_time == datetime.datetime(2023, 8, 16, 10, 0, tzinfo=dateutil.tz.tzutc())


def test_google_time_format():
    calendar = Calendar({'credentials_file_name': 'path_to_credentials.json'}, 'some_id')
    formatted_time = calendar.google_time_format(datetime.datetime(2023, 8, 16, 10, 0))
    assert formatted_time == '2023-08-16T10:00:00Z'


def test_collect_events(mock_google_calendar):
    # This test assumes mocked API call returns our sample_event
    calendar_events = [{'calendar_id': 'some_id', 'summary': 'Test Event'}]
    absent_events = []
    settings = {'credentials_file_name': 'path_to_credentials.json'}

    events, absents = collect_events(calendar_events, absent_events, settings)

    assert events[0][0]['summary'] == 'Test Event'
    assert dateutil.parser.parse(events[0][0]['start']['dateTime']) == datetime.datetime(2023, 8, 16, 10, 0, tzinfo=dateutil.tz.tzutc())
    assert dateutil.parser.parse(events[0][0]['end']['dateTime']) == datetime.datetime(2023, 8, 16, 11, 0, tzinfo=dateutil.tz.tzutc())

    assert absents == []


def test_get_credentials_http_valid(mock_google_calendar, monkeypatch):
    settings = {'credentials_file_name': 'path_to_credentials.json'}
    monkeypatch.setattr(os.path, "isfile", lambda x: True)
    mock_service_account_credentials = MagicMock()

    mock_service_account_credentials.authorize.return_value = "mocked_http_object"
    with patch("google_calendar.ServiceAccountCredentials.from_json_keyfile_name",
               return_value=mock_service_account_credentials):
        calendar = Calendar(settings, 'some_id')
    assert calendar.http is not None


def test_get_credentials_http_missing(mock_google_calendar, monkeypatch, capsys):
    settings = {'credentials_file_name': 'missing_path.json'}
    monkeypatch.setattr(os.path, "isfile", lambda x: False)
    calendar = Calendar(settings, 'some_id')
    assert calendar.http is None

    captured = capsys.readouterr()
    assert "Google API credentials file missing_path.json not found." in captured.out


def test_time_to_str(mock_google_calendar):
    settings = {'credentials_file_name': 'path_to_credentials.json'}
    calendar = Calendar(settings, 'some_id')

    test_time = datetime.datetime(2023, 8, 16, 10, 0)
    formatted_time = calendar.time_to_str(test_time)

    expected_suffix = f'-0{time.timezone // 3600}:00'
    assert formatted_time.endswith(expected_suffix)

