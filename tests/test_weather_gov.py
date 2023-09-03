import pytest
from unittest.mock import patch, Mock
from datetime import datetime
from xml.dom import minidom

from models import WeatherData
from weather_gov import Weather  # Adjust the import according to your setup

class TestWeather:

    # Mocking a successful weather XML response
    SUCCESS_XML = """
    <data>
        <temperature type="maximum">
            <value>30</value>
        </temperature>
        <temperature type="minimum">
            <value>20</value>
        </temperature>
        <icon-link>http://example.com/icon12.png</icon-link>
        <start-valid-time>2023-08-20T12:00:00</start-valid-time>
    </data>
    """

    # Mocking an error weather XML response
    ERROR_XML = """
    <data>
        <error>Some error message</error>
    </data>
    """

    @patch('weather_gov.urlopen')
    def test_get_weather_success(self, mock_urlopen):
        # Mocking the urlopen response with the success XML
        mock_urlopen.return_value.read.return_value = self.SUCCESS_XML

        weather = Weather()
        result = weather.get_weather(40.7128, -74.0060)

        assert result == WeatherData(
            temp_min=[20], temp_max=[30], icon=["icon"], day=[datetime.strptime("2023-08-20", "%Y-%m-%d")]
        )

    @patch('weather_gov.urlopen')
    def test_get_weather_error(self, mock_urlopen):
        # Mocking the urlopen response with the error XML
        mock_urlopen.return_value.read.return_value = self.ERROR_XML

        weather = Weather()
        result = weather.get_weather(40.7128, -74.0060)

        assert result is None
