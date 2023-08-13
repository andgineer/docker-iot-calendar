import pytest
from openweathermap_org import Weather, WEATHER_KEY_PARAM
from unittest.mock import patch, mock_open, Mock
import datetime


@pytest.mark.parametrize(
    "icon_code, condition_code, expected_icon",
    [
        ('01d', 800, 'skc'),  # testing common mapping
        ('10d', 500, 'ra1'),  # condition takes precedence over icon
        ('xxd', 761, 'dust'),  # invalid icon code, valid condition code
        ('02d', 9999, 'few'),  # valid icon code, invalid condition code
        ('xxd', 9999, '')     # invalid icon and condition codes
    ]
)
def test_openweathermap_icons(icon_code, condition_code, expected_icon):
    weather = Weather(settings={})  # Assuming empty settings because we won't be using the API in these tests
    result_icon = weather.openweathermap_icons(icon_code, condition_code)
    assert result_icon == expected_icon


def test_load_key_success():
    # Mocking os.path.isfile to always return True
    # and reading the file to return a valid JSON content
    with patch("os.path.isfile", return_value=True), \
         patch("builtins.open", mock_open(read_data='{"key": "test_key"}')):
        weather = Weather(settings={WEATHER_KEY_PARAM: "fake_path"})
        assert weather.key == "test_key"

def test_load_key_file_not_exists():
    with patch("os.path.isfile", return_value=False):
        weather = Weather(settings={WEATHER_KEY_PARAM: "nonexistent_path"})
        assert weather.key is None

def test_load_key_invalid_format():
    # Mocking the content of the file to be invalid (missing the 'key' field)
    with patch("os.path.isfile", return_value=True), \
         patch("builtins.open", mock_open(read_data='{"invalid_key": "test_value"}')):
        with pytest.raises(KeyError):
            Weather(settings={WEATHER_KEY_PARAM: "fake_path"})


def test_get_weather_success():
    mock_response = Mock()
    mock_response.json.return_value = {
        'cod': '200',
        'list': [
            {
                'dt_txt': '2023-08-13 12:00:00',
                'main': {'temp_min': 20.0, 'temp_max': 25.0},
                'weather': [{'icon': '01d', 'id': 800}]
            }
        ]
    }
    mock_response.text = '{"cod": "200", "list": ...}'

    with patch("requests.get", return_value=mock_response), patch.object(Weather, "load_key", return_value="dummy_key"):
        weather = Weather(settings={WEATHER_KEY_PARAM: "fake_path"})
        weather_data = weather.get_weather(51.5, 0.12)
        assert weather_data == {
            'temp_min': [20.0],
            'temp_max': [25.0],
            'icon': ['skc'],
            'day': [datetime.datetime(2023, 8, 13, 0, 0)]
        }


def test_get_weather_invalid_key():
    mock_response = Mock()
    mock_response.json.return_value = {
        'cod': '401',
        'message': 'Invalid API key. Please see http://openweathermap.org/faq#error401 for more info.'
    }

    with patch("requests.get", return_value=mock_response):
        weather = Weather(settings={WEATHER_KEY_PARAM: "fake_path"})
        weather_data = weather.get_weather(51.5, 0.12)
        assert weather_data is None

def test_get_weather_metric_units():
    mock_response = Mock()
    mock_response.json.return_value = {
        'cod': '200',
        'list': [{'dt_txt': '2023-08-13 12:00:00', 'main': {'temp_min': 20.0, 'temp_max': 25.0}, 'weather': [{'icon': '01d', 'id': 800}]}]
    }
    mock_response.text = '{"cod": "200", "list": ...}'

    with patch("requests.get", return_value=mock_response), patch.object(Weather, "load_key", return_value="dummy_key"):
        weather = Weather(settings={WEATHER_KEY_PARAM: "fake_path"})
        weather_data = weather.get_weather(51.5, 0.12, units='m')
        assert weather_data['temp_min'] == [20.0]
        assert weather_data['temp_max'] == [25.0]

def test_get_weather_shower_rain():
    mock_response = Mock()
    mock_response.json.return_value = {
        'cod': '200',
        'list': [{'dt_txt': '2023-08-13 12:00:00', 'main': {'temp_min': 18.0, 'temp_max': 22.0}, 'weather': [{'icon': '09d', 'id': 901}]}]
    }
    mock_response.text = '{"cod": "200", "list": ...}'

    with patch("requests.get", return_value=mock_response), patch.object(Weather, "load_key", return_value="dummy_key"):
        weather = Weather(settings={WEATHER_KEY_PARAM: "fake_path"})
        weather_data = weather.get_weather(51.5, 0.12)
        assert weather_data['icon'] == ['shra']
