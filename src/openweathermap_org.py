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
from models import WeatherData

WEATHER_KEY_PARAM = "openweathermap_key_file_name"
MIN_API_CALL_DELAY_SECONDS = 60 * 10


class Weather:
    """Load weather from OpenWeatherMap.org."""

    def __init__(self, props: Dict[str, Any]) -> None:
        """Init.

        :param props:
            settings['openweathermap_key_file_name'] - name and path of json file
            with "key", like

             {
             "key": "your key from https://home.openweathermap.org/users/sign_up"
             }
        """
        self.settings = props
        self.key = self.load_key()

    def load_key(self) -> Optional[str]:
        """Load the API key from the file specified in the settings.

        :return: The API key as a string, or None if the key couldn't be loaded.
        """
        if WEATHER_KEY_PARAM in self.settings and os.path.isfile(self.settings[WEATHER_KEY_PARAM]):
            with open(self.settings[WEATHER_KEY_PARAM], "r", encoding="utf8") as key_file:
                return json.loads(key_file.read())["key"]  # type: ignore
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
        cache_none=False,
    )
    def get_weather(
        self, latitude: float, longitude: float, days: int = 1, units: str = "m"
    ) -> Optional[WeatherData]:
        """Fetch weather data for the given latitude and longitude.

        :param latitude:
        :param longitude:
        :param days:
        :param units: m - metric, e - USA
        :return: None if no key or load error
        """
        if not self.key:
            print("Exiting because no API key")
            return None

        UNITS = {"e": "imperial", "m": "metric"}
        units_code = UNITS.get(units)
        if units_code is None:
            print(f"Exiting because unknown units '{units}', supported {UNITS}")
            return None

        params: Dict[str, Union[str, int, float]] = {
            "units": units_code,
            "lat": latitude,
            "lon": longitude,
            "appid": self.key,
        }
        weather_response = requests.get(
            "http://api.openweathermap.org/data/2.5/forecast",
            params=params,
            timeout=10,
        )

        print("Got weather from openweathermap.org:", weather_response.text[:100])
        weather_data = weather_response.json()

        if str(weather_data["cod"]) != "200":
            if str(weather_data["cod"]) == "401" and weather_data["message"].startswith(
                "Invalid API key"
            ):
                print(
                    "#" * 5,
                    f"""You should get your key from https://home.openweathermap.org/users/sign_up
                    and place it into {self.settings["openweathermap_key_file_name"]}""",
                )
            else:
                print("#" * 5, "ERROR:", weather_data["message"])
            return None

        highs: List[float] = []
        lows: List[float] = []
        icons = []
        dates: List[datetime.datetime] = []
        for weather_day in weather_data["list"]:
            date = datetime.datetime.strptime(weather_day["dt_txt"], "%Y-%m-%d %H:%M:%S")
            date = date.replace(hour=0, minute=0, second=0, microsecond=0)
            temp_min = weather_day["main"]["temp_min"]
            temp_max = weather_day["main"]["temp_max"]
            icon_code = weather_day["weather"][0]["icon"]
            condition_code = weather_day["weather"][0]["id"]
            icon = self.openweathermap_icons(icon_code, condition_code)
            if dates and dates[-1] == date:
                highs[-1] = max(highs[-1], temp_max)
                lows[-1] = min(lows[-1], temp_min)
            else:
                if len(dates) >= days:
                    break
                lows.append(temp_min)
                highs.append(temp_max)
                icons.append(icon)
                dates.append(date)

        return WeatherData(temp_min=lows, temp_max=highs, icon=icons, day=dates, images_folder="")


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    from iot_calendar import load_settings

    settings = load_settings(secrets_folder="../amazon-dash-private")
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))
    import time

    time.sleep(2)
    weather = Weather(settings)
    pprint(weather.get_weather("60.002228", "30.296947", days=4))
