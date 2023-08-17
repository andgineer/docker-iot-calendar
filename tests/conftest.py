import pytest


@pytest.fixture
def button_settings():
    return {
        "actions": [
            {"type": "click", "target": "#my-button"},
            {"type": "input", "target": ["#my-input"], "value": "{button}"},
        ],
        "summary": "Do something",
    }
