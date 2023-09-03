"""Load weather from weather.gov.

Works for USA only (NDFD regions).

Usage:
    Weather().get_weather(latitude, longitude)
"""

import datetime
from typing import List, Optional, Tuple
from urllib.request import urlopen
from xml.dom import minidom
from xml.dom.minicompat import NodeList
from xml.dom.minidom import Document, Element

from models import WeatherData


class InvalidXMLDataException(Exception):
    """Invalid XML data."""
    pass


class Weather:
    """Weather from weather.gov."""

    def get_weather(
        self, latitude: str, longitude: str, days: int = 1, units: str = "m"
    ) -> Optional[WeatherData]:
        """Get weather from weather.gov."""
        weather_xml = urlopen(
            f"http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?"
            f"whichClient=NDFDgenByDay&lat={latitude}&lon={longitude}"
            f"&format=24+hourly&numDays={days}&Unit={units}"
        ).read()
        dom = minidom.parseString(weather_xml)
        if dom.getElementsByTagName("error"):
            print(weather_xml)
            return None

        xml_temperatures = dom.getElementsByTagName("temperature")
        highs, lows = self.highs_and_lows(days, xml_temperatures)

        icons = self.get_day_icons(days, dom)
        if not icons:
            return None

        start_time_nodes = dom.getElementsByTagName("start-valid-time")
        if not start_time_nodes or not start_time_nodes[0].firstChild:
            return None
        xml_day_one = start_time_nodes[0].firstChild.nodeValue[:10]  # type: ignore
        day_one = datetime.datetime.strptime(xml_day_one, "%Y-%m-%d")
        day_list: List[datetime.datetime] = [
            (day_one + datetime.timedelta(days=i)) for i in range(days)
        ]

        return WeatherData(temp_min=lows, temp_max=highs, icon=icons, day=day_list)

    @staticmethod
    def get_day_icons(days: int, dom: Document) -> Optional[List[str]]:
        """Get icons for days."""
        icons: List[str] = []
        try:
            xml_icons = dom.getElementsByTagName("icon-link")
            for xml_icon in xml_icons:
                if not xml_icon.childNodes:
                    raise InvalidXMLDataException("xml_icon.firstChild is None.")
                if icon_value := xml_icon.childNodes[0].nodeValue:
                    icons.append(icon_value.split("/")[-1].split(".")[0].rstrip("0123456789"))
                else:
                    raise InvalidXMLDataException("nodeValue of xml_icon.firstChild is None.")
            if not icons:
                raise InvalidXMLDataException("xml_icons is None.")
            if len(icons) != days:
                raise InvalidXMLDataException(
                    f"Number of xml_icons ({len(icons)}) is not equal to days ({days})."
                )
        except (AttributeError, InvalidXMLDataException) as e:
            error_excerpt = dom.toprettyxml(indent="  ")[:200]
            print(f"Error accessing XML data: {e}. Excerpt:\n{error_excerpt}")
            return None
        return icons

    @staticmethod
    def highs_and_lows(
        days: int, xml_temperatures: NodeList[Element]
    ) -> Tuple[List[Optional[float]], List[Optional[float]]]:
        """Parse highs and lows from XML."""

        def extract_temperatures(item: Element, attribute_type: str) -> List[float]:
            """Extract temperatures from XML."""
            values: List[float] = []
            if item.getAttribute("type") == attribute_type:
                value_nodes = item.getElementsByTagName("value")
                for value in value_nodes:
                    if value.firstChild:
                        values.append(int(value.firstChild.nodeValue))  # type: ignore
            return values

        highs: List[Optional[float]] = [None] * days
        lows: List[Optional[float]] = [None] * days
        for item in xml_temperatures:
            max_values = extract_temperatures(item, "maximum")
            min_values = extract_temperatures(item, "minimum")

            if max_values:
                highs = max_values
            elif min_values:
                lows = min_values
        return highs, lows


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    weather = Weather()
    pprint(weather.get_weather("39.3286", "-76.6169", days=5))
