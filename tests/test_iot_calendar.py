import json
import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
import tornado.httputil
import tornado.web

from iot_calendar import Application, DashboardImageHandler, DashboardListHandler, load_settings
from models import WeatherData


# Sample test file for the load_settings function
def test_load_settings_no_file(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    mocker.patch("builtins.print")
    mocker.patch("sys.exit", side_effect=Exception("exit called"))

    with pytest.raises(Exception, match="exit called"):
        load_settings()


def test_load_settings_valid_file(mocker):
    mock_file_content = {"key": "value"}

    mocker.patch("os.path.isfile", return_value=True)
    mocker.patch("builtins.open", mocker.mock_open(read_data=json.dumps(mock_file_content)))

    settings = load_settings()

    assert settings == mock_file_content


def test_load_settings_with_missing_file(mocker, capsys):
    mocker.patch("os.path.isfile", return_value=False)
    with pytest.raises(SystemExit):
        load_settings()
    captured = capsys.readouterr()
    assert "No ../amazon-dash-private/settings.json found." in captured.out


class MockConnection:
    def __init__(self, *args, **kwargs):
        pass

    def write_headers(self, start_line, headers, chunk):
        pass

    def finish(self):
        pass

    def set_close_callback(self, callback):
        pass


@pytest.fixture
def mock_request_list_handler():
    mock_settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "../templates"),
        debug=True,
    )
    application = Application(settings=mock_settings)
    connection = MockConnection()
    request = tornado.httputil.HTTPServerRequest(
        method="GET", uri="/", version="HTTP/1.1", headers=None, body=None, connection=connection
    )
    handler = DashboardListHandler(application, request)
    handler._transforms = []
    handler.render = MagicMock()
    return handler


def test_disable_cache(mock_request_list_handler):
    mock_request_list_handler.disable_cache()
    assert mock_request_list_handler._headers.get("Cache-Control") == "no-cache, must-revalidate"
    assert mock_request_list_handler._headers.get("Expires") == "0"


@patch("iot_calendar.settings", {"dashboards": {}})
def test_dashboard_list_handler_renders_properly(mock_request_list_handler):
    # When: the get method of the DashboardListHandler is called
    mock_request_list_handler.get()

    # Then: assert that render was called correctly (or any other assertions you want to make)
    mock_request_list_handler.render.assert_called_once()


class MockWeather:
    def __init__(self, settings):
        pass

    def get_weather(self, latitude, longitude):
        return WeatherData(
            images_folder="mock/path",
            temp_min=[1, 2, 3],
            temp_max=[4, 5, 6],
            icon=["mock_icon"],
            day=[datetime(2020, 1, 1)],
        )


def test_load_params_default_values(mock_request_list_handler):
    params = mock_request_list_handler.load_params()

    assert params.dashboard == ""
    assert params.format == "png"
    assert params.style == "grayscale"


def test_load_params_overrides(mock_request_list_handler):
    params = mock_request_list_handler.load_params(dashboard="test_dash", format="jpeg")

    assert params.dashboard == "test_dash"
    assert params.format == "jpeg"


@pytest.fixture
def mock_request_inage_handler():
    mock_settings = dict(
        template_path=os.path.join(os.path.dirname(__file__), "../templates"),
        debug=True,
    )
    application = tornado.web.Application(settings=mock_settings)
    connection = MockConnection()
    request = tornado.httputil.HTTPServerRequest(
        method="GET", uri="/", version="HTTP/1.1", headers=None, body=None, connection=connection
    )

    # Change this line:
    handler = DashboardImageHandler(application, request)  # <-- use DashboardImageHandler here

    handler._transforms = []
    handler.render = MagicMock()
    return handler


@patch("iot_calendar.draw_calendar", return_value="mock_image_data")
@patch("iot_calendar.Weather", return_value=MockWeather({}))
@patch("iot_calendar.collect_events", return_value=("mock_events", "mock_absents"))
@patch("iot_calendar.events_to_weeks_grid", return_value="mock_grid")
@patch("iot_calendar.events_to_array", return_value=("mock_x", "mock_y"))
@patch("iot_calendar.dashboard_absent_events_list", return_value="mock_absent_events")
@patch("iot_calendar.calendar_events_list", return_value="mock_calendar_events")
@patch(
    "iot_calendar.settings",
    {
        "dashboards": {"default": {}},
        "latitude": "mock_latitude",
        "longitude": "mock_longitude",
        "images_folder": "mock_images_folder",
    },
)
def test_dashboard_image_handler(
    mock_calendar_events_list,
    mock_dashboard_absent_events_list,
    mock_events_to_array,
    mock_events_to_weeks_grid,
    mock_collect_events,
    MockWeather,
    mock_draw_calendar,
    mock_request_inage_handler,
):
    mock_request_inage_handler.get("png")

    mock_draw_calendar.assert_called_once()
    assert mock_request_inage_handler._headers.get("Content-type") == "image/png"
