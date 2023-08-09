import pytest
from datetime import datetime, timedelta

# Assuming calendar_data.py includes preprocess_actions function
from calendar_data import preprocess_actions, calendar_events_list, events_to_weeks_grid, events_to_array

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


def test_events_to_array_basic():
    start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    end_date = start_date + timedelta(days=1)
    events = [
        [{'start': start_date, 'end': end_date}],
    ]
    absents = []
    x, y = events_to_array(events, absents)
    assert x == [start_date]
    assert y == [[24*60]]  # Duration in minutes for a full day

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
