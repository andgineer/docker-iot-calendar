"""Load weather from weather.gov.

Works for USA only (NDFD regions).

Usage:
    Weather().get_weather(latitude, longitude)
"""

import datetime
from typing import Dict, List, Optional
from urllib.request import urlopen
from xml.dom import minidom


class Weather:
    """Weather from weather.gov."""

    def get_weather(
        self, latitude: str, longitude: str, days: int = 1, units: str = "m"
    ) -> Dict[str, List[Optional[int]]]:
        """Get weather from weather.gov.

        :param latitude:
        :param longitude:
        :param days:
        :param units: m - metric, e - USA
        :return:
         {'temp_min': [], 'temp_max': [], 'icon': [], 'day': []}
         with lists for each day
         or None if no key or load error
        """
        weather_xml = urlopen(
            f"http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?"
            f"whichClient=NDFDgenByDay&lat={latitude}&lon={longitude}"
            f"&format=24+hourly&numDays={days}&Unit={units}"
        ).read()
        dom = minidom.parseString(weather_xml)
        error = dom.getElementsByTagName("error")
        if error:
            print(weather_xml)
            return None

        # Parse temperatures
        xml_temperatures = dom.getElementsByTagName("temperature")
        highs = [None] * days
        lows = [None] * days
        for item in xml_temperatures:
            if item.getAttribute("type") == "maximum":
                values = item.getElementsByTagName("value")
                for i in range(len(values)):
                    highs[i] = int(values[i].firstChild.nodeValue)
            if item.getAttribute("type") == "minimum":
                values = item.getElementsByTagName("value")
                for i in range(len(values)):
                    lows[i] = int(values[i].firstChild.nodeValue)

        xml_icons = dom.getElementsByTagName("icon-link")
        icons = [None] * days
        for i, xml_icon in enumerate(xml_icons):
            icons[i] = (
                xml_icon.firstChild.nodeValue.split("/")[-1].split(".")[0].rstrip("0123456789")
            )

        xml_day_one = dom.getElementsByTagName("start-valid-time")[0].firstChild.nodeValue[:10]
        day_one = datetime.datetime.strptime(xml_day_one, "%Y-%m-%d")

        return {"temp_min": lows, "temp_max": highs, "icon": icons, "day": [day_one]}


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    weather = Weather()
    pprint(weather.get_weather("39.3286", "-76.6169"))
