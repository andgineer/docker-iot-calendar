import os.path
import sys
import pytest


sys.path.append(os.path.join(os.path.dirname(__file__), "../src"))


@pytest.fixture
def button_settings():
    return {
        "actions": [
            {"type": "click", "target": "#my-button"},
            {"type": "input", "target": ["#my-input"], "value": "{button}"},
        ],
        "summary": "Do something",
    }
