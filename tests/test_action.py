import json
from datetime import datetime, timedelta

import pytest
from dateutil.tz import tzoffset

# Assuming calendar_data.py includes preprocess_actions function
from calendar_data import dashboard_absent_events_list, preprocess_actions
from iot_calendar import calendar_events_list, events_to_array, events_to_weeks_grid


def test_preprocess_actions(button_settings):
    button = "My Button"
    expected_actions = [
        {"type": "click", "target": "#my-button", "summary": "Do something"},
        {
            "type": "input",
            "target": ["#my-input"],
            "value": "My Button",
            "summary": "Do something",
        },
    ]
    assert preprocess_actions(button, button_settings) == expected_actions


def test_preprocess_actions_basic():
    button_settings = {
        "actions": [
            {"type": "click", "target": "#{button}"},
            {"type": "input", "target": ["#{button}-input"], "value": "{button}"},
        ],
        "summary": "Do something",
    }
    button = "MyButton"
    expected_actions = [
        {"type": "click", "target": "#MyButton", "summary": "Do something"},
        {
            "type": "input",
            "target": ["#MyButton-input"],
            "value": "MyButton",
            "summary": "Do something",
        },
    ]
    assert preprocess_actions(button, button_settings) == expected_actions


def test_calendar_events_list_basic():
    settings = {
        "actions": {
            "MyButton": {
                "actions": [
                    {"type": "calendar", "dashboard": "TestDashboard", "summary": "Do something"}
                ]
            }
        }
    }
    dashboard_name = "TestDashboard"
    expected_result = [
        {"type": "calendar", "dashboard": "TestDashboard", "summary": "Do something"}
    ]
    assert calendar_events_list(settings, dashboard_name) == expected_result


def test_events_to_weeks_grid_empty():
    events = []
    absents = []
    result = events_to_weeks_grid(events, absents)
    # Ensure 4 weeks returned with each day having a 'values' list of length 0
    assert len(result) == 4
    for week in result:
        for day in week:
            assert day["values"] == []


def test_events_to_array_full_day():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    events = [
        [{"start": start_date, "end": end_date}],
    ]
    absents = []
    x, y = events_to_array(events, absents)
    assert x == [start_date]
    assert y == [[24 * 60]]  # Duration in minutes for a full day


def test_events_to_array_basic():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(minutes=1)
    events = [
        [{"start": start_date, "end": end_date}],
    ]
    absents = []
    x, y = events_to_array(events, absents)
    assert x == [start_date]
    assert y == [[1]]  # Duration in minutes


@pytest.mark.parametrize(
    "button,button_settings,expected",
    [
        (
            "MyButton",
            {
                "actions": [
                    {"type": "click", "target": "#{button}"},
                    {"type": "input", "target": ["#{button}-input"], "value": "{button}"},
                ],
                "summary": "Do something",
            },
            [
                {"type": "click", "target": "#MyButton", "summary": "Do something"},
                {
                    "type": "input",
                    "target": ["#MyButton-input"],
                    "value": "MyButton",
                    "summary": "Do something",
                },
            ],
        ),
    ],
)
def test_preprocess_actions_parametrized(button, button_settings, expected):
    assert preprocess_actions(button, button_settings) == expected


def test_preprocess_actions_substitution():
    button = "TestButton"
    settings = {
        "actions": [{"message": "{button} clicked"}, {"details": {"info": "You clicked {button}"}}]
    }
    expected_actions = [
        {"message": "TestButton clicked", "summary": "TestButton"},
        {"details": {"info": "You clicked TestButton"}, "summary": "TestButton"},
    ]
    assert preprocess_actions(button, settings) == expected_actions


def test_calendar_events_list_default():
    settings = {
        "actions": {
            "__DEFAULT__": {
                "actions": [
                    {
                        "type": "calendar",
                        "dashboard": "AnotherDashboard",
                        "summary": "Default action",
                    }
                ]
            }
        }
    }
    dashboard_name = "TestDashboard"
    assert calendar_events_list(settings, dashboard_name) == []


def test_dashboard_absent_events_list_no_absent():
    settings = {"dashboards": {"TestDashboard": {}}}
    dashboard_name = "TestDashboard"
    assert dashboard_absent_events_list(settings, dashboard_name) == []


def test_events_to_weeks_grid_multiple_weeks():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    events = [
        [{"start": start_date, "end": end_date}],
    ]
    absents = [
        [
            {
                "start": start_date - timedelta(days=21),
                "end": start_date - timedelta(days=1),
                "summary": "Vacation",
            }
        ]
    ]
    result = events_to_weeks_grid(events, absents, weeks=3)
    assert len(result) == 3  # Confirming 3 weeks
    assert result[-1][start_date.weekday()]["values"] == [
        1440
    ]  # Confirming the event's duration for the first day
    assert result[0][0]["values"] == [0]  # no events for the first day of the first week
    assert "absents" in result[0][0]  # Confirming the presence of an absence in the third week


with open("amazon-dash-private/settings.json", "r") as f:
    SETTINGS_DICT = json.load(f)


def mock_load_settings(*args, **kwargs):
    return SETTINGS_DICT


# 1. Setup a fixture
@pytest.fixture
def test_data():
    settings = mock_load_settings()

    events = [
        [
            {
                "end": datetime(2017, 4, 14, 8, 22, 30, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 14, 8, 15, 39, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 17, 8, 27, 43, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 17, 8, 16, 35, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 18, 8, 18, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 18, 8, 12, 9, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 19, 8, 24, 26, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 19, 8, 17, 8, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 20, 8, 22, 24, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 20, 8, 16, 34, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 21, 8, 25, 27, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 21, 8, 20, 26, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 22, 10, 16, 5, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 22, 10, 10, 7, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 23, 10, 43, 37, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 23, 10, 38, 45, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 24, 8, 22, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 24, 8, 14, 47, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
            {
                "end": datetime(2017, 4, 25, 8, 15, 7, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 25, 8, 10, 58, tzinfo=tzoffset(None, 10800)),
                "summary": "Morning work-out",
            },
        ],
        [
            {
                "end": datetime(2017, 4, 13, 20, 23, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 13, 20, 3, 5, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 14, 17, 26, 47, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 14, 16, 55, 56, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 16, 18, 20, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 16, 17, 48, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 17, 17, 51, 35, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 17, 17, 28, 31, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 19, 17, 21, 57, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 19, 16, 49, 55, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 21, 17, 5, 4, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 21, 16, 26, 51, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 23, 19, 18, 49, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 23, 18, 58, 12, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 4, 25, 20, 17, 14, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 25, 20, 3, 25, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 5, 10, 17, 59, 18, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 5, 10, 17, 36, 51, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
            {
                "end": datetime(2017, 5, 12, 20, 49, 9, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 5, 12, 20, 9, 32, tzinfo=tzoffset(None, 10800)),
                "summary": "Physiotherapy",
            },
        ],
    ]
    absents = [
        [
            {
                "end": datetime(2017, 5, 7, 23, 59, 59, tzinfo=tzoffset(None, 10800)),
                "start": datetime(2017, 4, 26, 0, 0, tzinfo=tzoffset(None, 10800)),
                "summary": "Sick",
            }
        ]
    ]

    return settings, events, absents


def test_load_settings(test_data):
    settings, _, _ = test_data
    # This will check if settings is not None or empty
    assert settings


def test_calendar_events_list(test_data):
    settings, _, _ = test_data
    result = calendar_events_list(settings, "anna_work_out")
    # For now, just ensuring it's not None or empty
    assert result is not None and len(result) > 0


def test_events_to_array(test_data):
    _, events, absents = test_data
    x, y = events_to_array(events, absents)

    # Add assertions based on expected output
    assert x is not None
    assert y is not None
    assert len(x) == 25
    assert len(y) == len(events)

    # You might add more specific assertions here based on expected values


def test_events_to_weeks_grid(test_data):
    _, events, absents = test_data
    weeks_num = 4
    grid = events_to_weeks_grid(events, absents, weeks=weeks_num)

    # Add assertions based on expected output
    assert grid is not None
    # For now, checking grid length. Depending on how events_to_weeks_grid works,
    # you might want more specific checks.
    assert len(grid) == weeks_num

    # You might add more specific assertions here based on expected values
