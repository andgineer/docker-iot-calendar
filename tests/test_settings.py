import json
import pytest

from google_calendar import GOOGLE_CREDENTIALS_PARAM
from iot_calendar import load_settings
from openweathermap_org import WEATHER_KEY_PARAM


def test_load_settings_images_and_dashboards(mocker):
    # Mock settings data
    dummy_settings = {
        "images_folder": "/dummy/path",
        "dashboards": {
            "dashboard1": {
                "image1": "test_image_1.jpg",
                "absent": [
                    {"image": "absent_image.jpg"}
                ]
            }
        },
        "events": {
            "event1": {
                "summary": [
                    {
                        "summary": "",
                        "image": "event_image.jpg"
                    }
                ],
                "actions": [
                    {"image": "action_image.jpg"}
                ]
            },
            "event2": {
              "summary": "{button}",
              "actions": []
            }
        }
    }

    # Mock necessary functions
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value=json.dumps(dummy_settings))
    mocker.patch("builtins.print")

    # Run load_settings
    settings = load_settings(load_secrets=False)

    # Assertions
    assert settings["images_folder"] == "/dummy/path"
    assert settings["dashboards"]["dashboard1"]["image1"] == "/dummy/path/test_image_1.jpg"
    assert settings["dashboards"]["dashboard1"]["absent"][0]["image"] == "/dummy/path/absent_image.jpg"
    assert settings["events"]["event1"]["summary"][0]["image"] == "/dummy/path/event_image.jpg"
    assert settings["events"]["event1"]["actions"][0]["image"] == "/dummy/path/action_image.jpg"


def test_load_settings_load_secrets(mocker):
    # Mock settings data
    dummy_settings = {
        GOOGLE_CREDENTIALS_PARAM: "/secrets_path/google_credentials.json",
        WEATHER_KEY_PARAM: "/secrets_path/weather_key.json"
    }

    # Mock necessary functions
    mocker.patch("pathlib.Path.is_file", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value=json.dumps(dummy_settings))
    mocker.patch("builtins.print")

    # Run load_settings
    settings = load_settings()

    # Assertions
    assert settings[GOOGLE_CREDENTIALS_PARAM] == "../amazon-dash-private/google_credentials.json"
    assert settings[WEATHER_KEY_PARAM] == "../amazon-dash-private/weather_key.json"


def test_load_settings_no_file_result_in_exit(mocker):
    mocker.patch("pathlib.Path.is_file", return_value=False)
    mocker.patch("builtins.print")
    mocker.patch("sys.exit", side_effect=Exception("exit called"))

    with pytest.raises(Exception, match="exit called"):
        load_settings()


def test_load_settings_no_file_print_error(mocker, capsys):
    mocker.patch("pathlib.Path.is_file", return_value=False)
    with pytest.raises(SystemExit):
        load_settings()
    captured = capsys.readouterr()
    assert "settings.json found." in captured.out


def test_load_settings_valid_file(mocker):
    mock_file_content = {"key": "value"}

    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("pathlib.Path.read_text", return_value=json.dumps(mock_file_content))

    settings = load_settings(load_secrets=False)

    assert settings == mock_file_content
