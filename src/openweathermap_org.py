"""Load weather from OpenWeatherMap.org.

Usage:
    Weather(settings).get_weather(latitude, longitude)

"""
import datetime
import json
import os.path
from typing import Any, Dict, List, Optional, Union

import requests

from cached_decorator import cached

WEATHER_KEY_PARAM = "openweathermap_key_file_name"
MIN_API_CALL_DELAY_SECONDS = 60 * 10


class Weather:
    """Load weather from OpenWeatherMap.org."""

    def __init__(self, settings: Dict[str, Any]) -> None:
        """Init.

        :param settings:
            settings['openweathermap_key_file_name'] - name and path of json file
            with "key", like

             {
             "key": "your key from https://home.openweathermap.org/users/sign_up"
             }
        """
        self.settings = settings
        self.key = self.load_key()

    def load_key(self) -> Optional[str]:
        """Load the API key from the file specified in the settings.

        :return: The API key as a string, or None if the key couldn't be loaded.
        """
        if WEATHER_KEY_PARAM in self.settings and os.path.isfile(self.settings[WEATHER_KEY_PARAM]):
            with open(self.settings[WEATHER_KEY_PARAM], "r", encoding="utf8") as key_file:
                return json.loads(key_file.read())["key"]
        else:
            return None

    def openweathermap_icons(self, icon_code: str, condition_code: Union[str, int]) -> str:
        """Convert OpenWeatherMap icon code and condition code to icon file names.

        Mostly we use icon code but for specific conditions use specific icon.
        Full codes list: http://openweathermap.org/weather-conditions
        """
        icons_map = {
            "01": "skc",  # clear
            "02": "few",
            "03": "sct",  # scattered
            "04": "ovc",  # overcast clouds & broken clouds
            "09": "shra",  # shower rain
            "10": "hi_shwrs",  # ligt rain
            "11": "tsra",  # thunderstorm
            "13": "sn",  # snow
            "50": "mist",  # mist
        }
        conditions_map = {
            "511": "fzra",  # freezing rain
            "741": "fg",  # fog
            "761": "dust",
            "906": "ip",  # hail
            "615": "mix",  # snow and light rain
            "616": "rasn",  # snow and rain
            "900": "nsurtsra",  # tornado
            "902": "nsurtsra",  # hurricane
            "500": "ra1",  # light rain
            "501": "ra1",  # moderate rain
            "711": "smoke",
            "905": "wind",
            "957": "wind",
        }
        return conditions_map.get(str(condition_code), icons_map.get(icon_code[:-1], ""))

    @cached(
        seconds=MIN_API_CALL_DELAY_SECONDS,
        trace_fmt="Use stored weather data without calling openweathermap API (from {time})",
        daily_refresh=True,
        per_instance=True,
    )
    def get_weather(
        self, latitude: float, longitude: float, days: int = 1, units: str = "m"
    ) -> Optional[Dict[str, Union[List[float], List[str], List[datetime.datetime]]]]:
        """Fetch weather data for the given latitude and longitude.

        :param latitude:
        :param longitude:
        :param days:
        :param units: m - metric, e - USA
        :return:
         {'temp_min': [], 'temp_max': [], 'icon': [], 'day': []}
         or None if no key or load error
        """
        if not self.key:
            print("Exiting because no API key")
            return None

        UNITS = {"e": "imperial", "m": "metric"}
        units_code = UNITS.get(units)
        if units_code is None:
            print(f"Exiting because unknown units '{units}', supported {UNITS}")
            return None

        weather_response = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast",
            params={"units": units_code, "lat": latitude, "lon": longitude, "appid": self.key},
            timeout=10,
        )
        print("Got weather from openweathermap.org:", weather_response.text[:100])
        weather = weather_response.json()

        if str(weather["cod"]) != "200":
            if str(weather["cod"]) == "401" and weather["message"].startswith("Invalid API key"):
                print(
                    "#" * 5,
                    f"""You should get your key from https://home.openweathermap.org/users/sign_up
                    and place it into {self.settings["openweathermap_key_file_name"]}""",
                )
            else:
                print("#" * 5, "ERROR:", weather["message"])
            return None

        highs = []
        lows = []
        icons = []
        dates = []
        for weather_day in weather["list"]:
            date = datetime.datetime.strptime(weather_day["dt_txt"], "%Y-%m-%d %H:%M:%S")
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            temp_min = weather_day["main"]["temp_min"]
            temp_max = weather_day["main"]["temp_max"]
            icon_code = weather_day["weather"][0]["icon"]
            condition_code = weather_day["weather"][0]["id"]
            icon = self.openweathermap_icons(icon_code, condition_code)
            if dates and dates[-1] == date:
                if highs[-1] < temp_max:
                    highs[-1] = temp_max
                if lows[-1] > temp_min:
                    lows[-1] = temp_min
            else:
                if len(dates) >= days:
                    break
                lows.append(temp_min)
                highs.append(temp_max)
                icons.append(icon)
                dates.append(date)

        return {"temp_min": lows, "temp_max": highs, "icon": icons, "day": dates}


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    from iot_calendar import load_settings

    settings = load_settings(secrets_folder="../secrets")
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))
    import time

    time.sleep(2)
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))

    test_response = {
        "cod": "200",
        "message": 0.1318,
        "cnt": 37,
        "list": [
            {
                "dt": 1492851600,
                "main": {
                    "temp": 4.82,
                    "temp_min": 4.82,
                    "temp_max": 5.36,
                    "pressure": 1001.09,
                    "sea_level": 1003.73,
                    "grnd_level": 1001.09,
                    "humidity": 96,
                    "temp_kf": -0.54,
                },
                "weather": [
                    {"id": 802, "main": "Clouds", "description": "scattered clouds", "icon": "03d"}
                ],
                "clouds": {"all": 36},
                "wind": {"speed": 1.82, "deg": 221.003},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-22 09:00:00",
            },
            {
                "dt": 1492862400,
                "main": {
                    "temp": 6.23,
                    "temp_min": 6.23,
                    "temp_max": 6.64,
                    "pressure": 1001.21,
                    "sea_level": 1003.85,
                    "grnd_level": 1001.21,
                    "humidity": 85,
                    "temp_kf": -0.41,
                },
                "weather": [
                    {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}
                ],
                "clouds": {"all": 76},
                "wind": {"speed": 1.62, "deg": 77.002},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-22 12:00:00",
            },
            {
                "dt": 1492873200,
                "main": {
                    "temp": 5.75,
                    "temp_min": 5.75,
                    "temp_max": 6.02,
                    "pressure": 1001.54,
                    "sea_level": 1004.33,
                    "grnd_level": 1001.54,
                    "humidity": 79,
                    "temp_kf": -0.27,
                },
                "weather": [
                    {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04d"}
                ],
                "clouds": {"all": 64},
                "wind": {"speed": 2.47, "deg": 57.5049},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-22 15:00:00",
            },
            {
                "dt": 1492884000,
                "main": {
                    "temp": 2.2,
                    "temp_min": 2.2,
                    "temp_max": 2.34,
                    "pressure": 1002.61,
                    "sea_level": 1005.5,
                    "grnd_level": 1002.61,
                    "humidity": 86,
                    "temp_kf": -0.14,
                },
                "weather": [
                    {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04n"}
                ],
                "clouds": {"all": 80},
                "wind": {"speed": 1.61, "deg": 25.5019},
                "rain": {},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-22 18:00:00",
            },
            {
                "dt": 1492894800,
                "main": {
                    "temp": -0.58,
                    "temp_min": -0.58,
                    "temp_max": -0.58,
                    "pressure": 1003.55,
                    "sea_level": 1006.33,
                    "grnd_level": 1003.55,
                    "humidity": 88,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04n"}
                ],
                "clouds": {"all": 56},
                "wind": {"speed": 1.36, "deg": 320.003},
                "rain": {},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-22 21:00:00",
            },
            {
                "dt": 1492905600,
                "main": {
                    "temp": -2.51,
                    "temp_min": -2.51,
                    "temp_max": -2.51,
                    "pressure": 1004.21,
                    "sea_level": 1007.13,
                    "grnd_level": 1004.21,
                    "humidity": 85,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 803, "main": "Clouds", "description": "broken clouds", "icon": "04n"}
                ],
                "clouds": {"all": 64},
                "wind": {"speed": 1.22, "deg": 283.002},
                "rain": {},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-23 00:00:00",
            },
            {
                "dt": 1492916400,
                "main": {
                    "temp": -2.86,
                    "temp_min": -2.86,
                    "temp_max": -2.86,
                    "pressure": 1005.28,
                    "sea_level": 1008.13,
                    "grnd_level": 1005.28,
                    "humidity": 84,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 802, "main": "Clouds", "description": "scattered clouds", "icon": "03d"}
                ],
                "clouds": {"all": 48},
                "wind": {"speed": 1.25, "deg": 271.501},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-23 03:00:00",
            },
            {
                "dt": 1492927200,
                "main": {
                    "temp": 2.72,
                    "temp_min": 2.72,
                    "temp_max": 2.72,
                    "pressure": 1006.9,
                    "sea_level": 1009.62,
                    "grnd_level": 1006.9,
                    "humidity": 97,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}
                ],
                "clouds": {"all": 20},
                "wind": {"speed": 1.76, "deg": 326.001},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-23 06:00:00",
            },
            {
                "dt": 1492938000,
                "main": {
                    "temp": 6.38,
                    "temp_min": 6.38,
                    "temp_max": 6.38,
                    "pressure": 1008.45,
                    "sea_level": 1011.21,
                    "grnd_level": 1008.45,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}
                ],
                "clouds": {"all": 24},
                "wind": {"speed": 1.31, "deg": 299.003},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-23 09:00:00",
            },
            {
                "dt": 1492948800,
                "main": {
                    "temp": 5.46,
                    "temp_min": 5.46,
                    "temp_max": 5.46,
                    "pressure": 1010.02,
                    "sea_level": 1012.79,
                    "grnd_level": 1010.02,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 56},
                "wind": {"speed": 2.91, "deg": 292.501},
                "rain": {"3h": 1.005},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-23 12:00:00",
            },
            {
                "dt": 1492959600,
                "main": {
                    "temp": 4.33,
                    "temp_min": 4.33,
                    "temp_max": 4.33,
                    "pressure": 1011.82,
                    "sea_level": 1014.54,
                    "grnd_level": 1011.82,
                    "humidity": 93,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 64},
                "wind": {"speed": 3.56, "deg": 278.004},
                "rain": {"3h": 0.015},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-23 15:00:00",
            },
            {
                "dt": 1492970400,
                "main": {
                    "temp": 1.33,
                    "temp_min": 1.33,
                    "temp_max": 1.33,
                    "pressure": 1013.24,
                    "sea_level": 1016.02,
                    "grnd_level": 1013.24,
                    "humidity": 89,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 56},
                "wind": {"speed": 2.97, "deg": 270},
                "rain": {"3h": 0.0049999999999999},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-23 18:00:00",
            },
            {
                "dt": 1492981200,
                "main": {
                    "temp": 0.34,
                    "temp_min": 0.34,
                    "temp_max": 0.34,
                    "pressure": 1014.39,
                    "sea_level": 1017.16,
                    "grnd_level": 1014.39,
                    "humidity": 93,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 88},
                "wind": {"speed": 3.1, "deg": 261.5},
                "rain": {"3h": 0.105},
                "snow": {"3h": 0.2765},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-23 21:00:00",
            },
            {
                "dt": 1492992000,
                "main": {
                    "temp": 0.01,
                    "temp_min": 0.01,
                    "temp_max": 0.01,
                    "pressure": 1015.06,
                    "sea_level": 1017.88,
                    "grnd_level": 1015.06,
                    "humidity": 98,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 2.56, "deg": 265.008},
                "rain": {"3h": 0.0049999999999999},
                "snow": {"3h": 2.0675},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-24 00:00:00",
            },
            {
                "dt": 1493002800,
                "main": {
                    "temp": -0.41,
                    "temp_min": -0.41,
                    "temp_max": -0.41,
                    "pressure": 1015.6,
                    "sea_level": 1018.41,
                    "grnd_level": 1015.6,
                    "humidity": 98,
                    "temp_kf": 0,
                },
                "weather": [{"id": 601, "main": "Snow", "description": "snow", "icon": "13d"}],
                "clouds": {"all": 92},
                "wind": {"speed": 1.96, "deg": 216.501},
                "rain": {},
                "snow": {"3h": 5.4125},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-24 03:00:00",
            },
            {
                "dt": 1493013600,
                "main": {
                    "temp": 0.56,
                    "temp_min": 0.56,
                    "temp_max": 0.56,
                    "pressure": 1016.38,
                    "sea_level": 1019.16,
                    "grnd_level": 1016.38,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 600, "main": "Snow", "description": "light snow", "icon": "13d"}
                ],
                "clouds": {"all": 44},
                "wind": {"speed": 1.96, "deg": 209.504},
                "rain": {},
                "snow": {"3h": 1.2025},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-24 06:00:00",
            },
            {
                "dt": 1493024400,
                "main": {
                    "temp": 3.19,
                    "temp_min": 3.19,
                    "temp_max": 3.19,
                    "pressure": 1017.12,
                    "sea_level": 1019.84,
                    "grnd_level": 1017.12,
                    "humidity": 99,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                ],
                "clouds": {"all": 12},
                "wind": {"speed": 1.78, "deg": 200.505},
                "rain": {},
                "snow": {"3h": 0.0025000000000013},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-24 09:00:00",
            },
            {
                "dt": 1493035200,
                "main": {
                    "temp": 4.07,
                    "temp_min": 4.07,
                    "temp_max": 4.07,
                    "pressure": 1017.47,
                    "sea_level": 1020.34,
                    "grnd_level": 1017.47,
                    "humidity": 97,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 76},
                "wind": {"speed": 1.31, "deg": 253.501},
                "rain": {"3h": 0.055},
                "snow": {"3h": 0.0024999999999995},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-24 12:00:00",
            },
            {
                "dt": 1493046000,
                "main": {
                    "temp": 3.02,
                    "temp_min": 3.02,
                    "temp_max": 3.02,
                    "pressure": 1018.2,
                    "sea_level": 1021.03,
                    "grnd_level": 1018.2,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 80},
                "wind": {"speed": 1.41, "deg": 261.501},
                "rain": {"3h": 1.005},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-24 15:00:00",
            },
            {
                "dt": 1493056800,
                "main": {
                    "temp": 0.94,
                    "temp_min": 0.94,
                    "temp_max": 0.94,
                    "pressure": 1018.93,
                    "sea_level": 1021.85,
                    "grnd_level": 1018.93,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 76},
                "wind": {"speed": 1.35, "deg": 240.5},
                "rain": {"3h": 0.35},
                "snow": {"3h": 0.029999999999999},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-24 18:00:00",
            },
            {
                "dt": 1493067600,
                "main": {
                    "temp": -1.87,
                    "temp_min": -1.87,
                    "temp_max": -1.87,
                    "pressure": 1019.39,
                    "sea_level": 1022.18,
                    "grnd_level": 1019.39,
                    "humidity": 98,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 48},
                "wind": {"speed": 1.16, "deg": 190.501},
                "rain": {"3h": 0.0099999999999998},
                "snow": {"3h": 0.035},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-24 21:00:00",
            },
            {
                "dt": 1493078400,
                "main": {
                    "temp": -1.91,
                    "temp_min": -1.91,
                    "temp_max": -1.91,
                    "pressure": 1019.59,
                    "sea_level": 1022.42,
                    "grnd_level": 1019.59,
                    "humidity": 95,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 600, "main": "Snow", "description": "light snow", "icon": "13n"}
                ],
                "clouds": {"all": 88},
                "wind": {"speed": 1.22, "deg": 159.5},
                "rain": {},
                "snow": {"3h": 0.06},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-25 00:00:00",
            },
            {
                "dt": 1493089200,
                "main": {
                    "temp": -1.8,
                    "temp_min": -1.8,
                    "temp_max": -1.8,
                    "pressure": 1019.66,
                    "sea_level": 1022.51,
                    "grnd_level": 1019.66,
                    "humidity": 94,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 600, "main": "Snow", "description": "light snow", "icon": "13d"}
                ],
                "clouds": {"all": 48},
                "wind": {"speed": 1.26, "deg": 127.002},
                "rain": {},
                "snow": {"3h": 0.050000000000001},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-25 03:00:00",
            },
            {
                "dt": 1493100000,
                "main": {
                    "temp": 2.35,
                    "temp_min": 2.35,
                    "temp_max": 2.35,
                    "pressure": 1019.82,
                    "sea_level": 1022.55,
                    "grnd_level": 1019.82,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 800, "main": "Clear", "description": "clear sky", "icon": "01d"}
                ],
                "clouds": {"all": 0},
                "wind": {"speed": 1.77, "deg": 112},
                "rain": {},
                "snow": {"3h": 0.004999999999999},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-25 06:00:00",
            },
            {
                "dt": 1493110800,
                "main": {
                    "temp": 5.94,
                    "temp_min": 5.94,
                    "temp_max": 5.94,
                    "pressure": 1019.33,
                    "sea_level": 1022.07,
                    "grnd_level": 1019.33,
                    "humidity": 98,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 801, "main": "Clouds", "description": "few clouds", "icon": "02d"}
                ],
                "clouds": {"all": 12},
                "wind": {"speed": 2.76, "deg": 126.501},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-25 09:00:00",
            },
            {
                "dt": 1493121600,
                "main": {
                    "temp": 6.91,
                    "temp_min": 6.91,
                    "temp_max": 6.91,
                    "pressure": 1018.4,
                    "sea_level": 1021.15,
                    "grnd_level": 1018.4,
                    "humidity": 85,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 802, "main": "Clouds", "description": "scattered clouds", "icon": "03d"}
                ],
                "clouds": {"all": 48},
                "wind": {"speed": 4.2, "deg": 134.009},
                "rain": {},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-25 12:00:00",
            },
            {
                "dt": 1493132400,
                "main": {
                    "temp": 5.12,
                    "temp_min": 5.12,
                    "temp_max": 5.12,
                    "pressure": 1017.61,
                    "sea_level": 1020.33,
                    "grnd_level": 1017.61,
                    "humidity": 90,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 4.67, "deg": 136.002},
                "rain": {"3h": 0.385},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-25 15:00:00",
            },
            {
                "dt": 1493143200,
                "main": {
                    "temp": 3.47,
                    "temp_min": 3.47,
                    "temp_max": 3.47,
                    "pressure": 1016.48,
                    "sea_level": 1019.3,
                    "grnd_level": 1016.48,
                    "humidity": 93,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 4.58, "deg": 139.5},
                "rain": {"3h": 1},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-25 18:00:00",
            },
            {
                "dt": 1493154000,
                "main": {
                    "temp": 3.45,
                    "temp_min": 3.45,
                    "temp_max": 3.45,
                    "pressure": 1014.92,
                    "sea_level": 1017.68,
                    "grnd_level": 1014.92,
                    "humidity": 95,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 3.65, "deg": 138.501},
                "rain": {"3h": 2.39},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-25 21:00:00",
            },
            {
                "dt": 1493164800,
                "main": {
                    "temp": 4.8,
                    "temp_min": 4.8,
                    "temp_max": 4.8,
                    "pressure": 1013.14,
                    "sea_level": 1015.83,
                    "grnd_level": 1013.14,
                    "humidity": 92,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 3.46, "deg": 155.504},
                "rain": {"3h": 1.79},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-26 00:00:00",
            },
            {
                "dt": 1493175600,
                "main": {
                    "temp": 5.57,
                    "temp_min": 5.57,
                    "temp_max": 5.57,
                    "pressure": 1011.35,
                    "sea_level": 1013.99,
                    "grnd_level": 1011.35,
                    "humidity": 92,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 3.41, "deg": 151.501},
                "rain": {"3h": 2.08},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-26 03:00:00",
            },
            {
                "dt": 1493186400,
                "main": {
                    "temp": 8.33,
                    "temp_min": 8.33,
                    "temp_max": 8.33,
                    "pressure": 1010.51,
                    "sea_level": 1013.28,
                    "grnd_level": 1010.51,
                    "humidity": 95,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 5.19, "deg": 188.5},
                "rain": {"3h": 1.18},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-26 06:00:00",
            },
            {
                "dt": 1493197200,
                "main": {
                    "temp": 9.95,
                    "temp_min": 9.95,
                    "temp_max": 9.95,
                    "pressure": 1011.86,
                    "sea_level": 1014.44,
                    "grnd_level": 1011.86,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 4.21, "deg": 209.004},
                "rain": {"3h": 1.53},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-26 09:00:00",
            },
            {
                "dt": 1493208000,
                "main": {
                    "temp": 9.97,
                    "temp_min": 9.97,
                    "temp_max": 9.97,
                    "pressure": 1012.61,
                    "sea_level": 1015.32,
                    "grnd_level": 1012.61,
                    "humidity": 100,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 76},
                "wind": {"speed": 3.6, "deg": 200.503},
                "rain": {"3h": 1.4},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-26 12:00:00",
            },
            {
                "dt": 1493218800,
                "main": {
                    "temp": 9.14,
                    "temp_min": 9.14,
                    "temp_max": 9.14,
                    "pressure": 1013.26,
                    "sea_level": 1015.92,
                    "grnd_level": 1013.26,
                    "humidity": 99,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10d"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 2.75, "deg": 255.504},
                "rain": {"3h": 1.02},
                "snow": {},
                "sys": {"pod": "d"},
                "dt_txt": "2017-04-26 15:00:00",
            },
            {
                "dt": 1493229600,
                "main": {
                    "temp": 5.9,
                    "temp_min": 5.9,
                    "temp_max": 5.9,
                    "pressure": 1014.74,
                    "sea_level": 1017.42,
                    "grnd_level": 1014.74,
                    "humidity": 98,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 4.01, "deg": 263.005},
                "rain": {"3h": 2.44},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-26 18:00:00",
            },
            {
                "dt": 1493240400,
                "main": {
                    "temp": 3.77,
                    "temp_min": 3.77,
                    "temp_max": 3.77,
                    "pressure": 1016.91,
                    "sea_level": 1019.69,
                    "grnd_level": 1016.91,
                    "humidity": 93,
                    "temp_kf": 0,
                },
                "weather": [
                    {"id": 500, "main": "Rain", "description": "light rain", "icon": "10n"}
                ],
                "clouds": {"all": 92},
                "wind": {"speed": 4.51, "deg": 240.002},
                "rain": {"3h": 0.98},
                "snow": {},
                "sys": {"pod": "n"},
                "dt_txt": "2017-04-26 21:00:00",
            },
        ],
        "city": {
            "id": 519711,
            "name": "Novaya Derevnya",
            "coord": {"lat": 59.9953, "lon": 30.2878},
            "country": "RU",
        },
    }
