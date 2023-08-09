import pytest
from datetime import datetime, timedelta

# Assuming calendar_data.py includes preprocess_actions function
from calendar_data import preprocess_actions, calendar_events_list, events_to_weeks_grid, events_to_array, \
    dashboard_absent_events_list


def test_preprocess_actions(button_settings):
    button = 'My Button'
    expected_actions = [
        {'type': 'click', 'target': '#my-button', 'summary': 'Do something'},
        {'type': 'input', 'target': ['#my-input'], 'value': 'My Button', 'summary': 'Do something'},
    ]
    assert preprocess_actions(button, button_settings) == expected_actions


def test_preprocess_actions_basic():
    button_settings = {
        'actions': [
            {'type': 'click', 'target': '#{button}'},
            {'type': 'input', 'target': ['#{button}-input'], 'value': '{button}'},
        ],
        'summary': 'Do something'
    }
    button = 'MyButton'
    expected_actions = [
        {'type': 'click', 'target': '#MyButton', 'summary': 'Do something'},
        {'type': 'input', 'target': ['#MyButton-input'], 'value': 'MyButton', 'summary': 'Do something'},
    ]
    assert preprocess_actions(button, button_settings) == expected_actions


def test_calendar_events_list_basic():
    settings = {
        'actions': {
            'MyButton': {
                'actions': [
                    {'type': 'calendar', 'dashboard': 'TestDashboard', 'summary': 'Do something'}
                ]
            }
        }
    }
    dashboard_name = 'TestDashboard'
    expected_result = [{'type': 'calendar', 'dashboard': 'TestDashboard', 'summary': 'Do something'}]
    assert calendar_events_list(settings, dashboard_name) == expected_result


def test_events_to_weeks_grid_empty():
    events = []
    absents = []
    result = events_to_weeks_grid(events, absents)
    # Ensure 4 weeks returned with each day having a 'values' list of length 0
    assert len(result) == 4
    for week in result:
        for day in week:
            assert day['values'] == []


def test_events_to_array_full_day():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    events = [
        [{'start': start_date, 'end': end_date}],
    ]
    absents = []
    x, y = events_to_array(events, absents)
    assert x == [start_date]
    assert y == [[24*60]]  # Duration in minutes for a full day


def test_events_to_array_basic():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(minutes=1)
    events = [
        [{'start': start_date, 'end': end_date}],
    ]
    absents = []
    x, y = events_to_array(events, absents)
    assert x == [start_date]
    assert y == [[1]]  # Duration in minutes


@pytest.mark.parametrize("button,button_settings,expected", [
    ("MyButton", {
        'actions': [
            {'type': 'click', 'target': '#{button}'},
            {'type': 'input', 'target': ['#{button}-input'], 'value': '{button}'},
        ],
        'summary': 'Do something'
    }, [
        {'type': 'click', 'target': '#MyButton', 'summary': 'Do something'},
        {'type': 'input', 'target': ['#MyButton-input'], 'value': 'MyButton', 'summary': 'Do something'},
    ]),
])
def test_preprocess_actions_parametrized(button, button_settings, expected):
    assert preprocess_actions(button, button_settings) == expected


def test_preprocess_actions_substitution():
    button = 'TestButton'
    settings = {
        'actions': [
            {'message': '{button} clicked'},
            {'details': {'info': 'You clicked {button}'}}
        ]
    }
    expected_actions = [
        {'message': 'TestButton clicked', 'summary': 'TestButton'},
        {'details': {'info': 'You clicked TestButton'}, 'summary': 'TestButton'}
    ]
    assert preprocess_actions(button, settings) == expected_actions


def test_calendar_events_list_default():
    settings = {
        'actions': {
            '__DEFAULT__': {
                'actions': [
                    {'type': 'calendar', 'dashboard': 'AnotherDashboard', 'summary': 'Default action'}
                ]
            }
        }
    }
    dashboard_name = 'TestDashboard'
    assert calendar_events_list(settings, dashboard_name) == []


def test_dashboard_absent_events_list_no_absent():
    settings = {
        'dashboards': {
            'TestDashboard': {}
        }
    }
    dashboard_name = 'TestDashboard'
    assert dashboard_absent_events_list(settings, dashboard_name) == []


def test_events_to_weeks_grid_multiple_weeks():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    events = [
        [{'start': start_date, 'end': end_date}],
    ]
    absents = [[{'start': start_date - timedelta(days=14), 'end': start_date - timedelta(days=1), 'summary': 'Vacation'}]]
    result = events_to_weeks_grid(events, absents, weeks=3)
    assert len(result) == 3  # Confirming 3 weeks
    assert result[-1][start_date.weekday()]['values'] == [1440]  # Confirming the event's duration for the first day
    assert result[0][0]['values'] == [0]  # no events for the first day of the first week
    assert 'absents' in result[2][0]  # Confirming the presence of an absence in the third week
