from calendar_data import preprocess_actions


def test_preprocess_actions(button_settings):
    button = 'My Button'
    expected_actions = [
        {'type': 'click', 'target': '#my-button', 'summary': 'Do something'},
        {'type': 'input', 'target': ['#my-input'], 'value': 'My Button', 'summary': 'Do something'},
    ]
    assert preprocess_actions(button, button_settings) == expected_actions
