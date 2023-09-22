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


class Weather:
    """Weather from weather.gov."""

    def get_weather(
        self, latitude: str, longitude: str, days: int = 1, units: str = "m"
    ) -> Optional[WeatherData]:
        """Get weather from weather.gov.

        For days more than 1 it returns "No data were found using the following input"
        """
        try:
            url = (
                f"http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?"
                f"whichClient=NDFDgenByDay&lat={latitude}&lon={longitude}"
                f"&format=24+hourly&numDays={days}&Unit={units}"
            )
            with urlopen(url) as response:
                weather_xml = response.read()
            dom = minidom.parseString(weather_xml)
            if error := dom.getElementsByTagName("error"):
                print(
                    f"Error getting weather from weather.gov: {error}\n{dom.toprettyxml(indent='  ')}"
                )
                return None
        except Exception as e:
            print(f"Error extracting weather from weather.gov: {e}")
            return None
        try:
            xml_temperatures = dom.getElementsByTagName("temperature")
            highs, lows = self.highs_and_lows(days, xml_temperatures)
            icons = self.get_day_icons(days, dom)
            start_time_nodes = dom.getElementsByTagName("start-valid-time")
            if not start_time_nodes or not start_time_nodes[0].firstChild:
                raise InvalidXMLDataException("start-valid-time is None.")
            xml_day_one = start_time_nodes[0].firstChild.nodeValue[:10]  # type: ignore
            day_one = datetime.datetime.strptime(xml_day_one, "%Y-%m-%d")
            day_list: List[datetime.datetime] = [
                (day_one + datetime.timedelta(days=i)) for i in range(days)
            ]
            return WeatherData(
                temp_min=lows, temp_max=highs, icon=icons, day=day_list, images_folder=""
            )
        except InvalidXMLDataException as e:
            error_excerpt = dom.toprettyxml(indent="  ")[:10000]
            print(f"Error extracting weather from weather.gov: {e}\n{error_excerpt}")
            return None

    @staticmethod
    def get_day_icons(days: int, dom: Document) -> List[str]:
        """Get icons for days."""
        icons: List[str] = []
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
        return icons

    @staticmethod
    def highs_and_lows(
        days: int, xml_temperatures: NodeList[Element]
    ) -> Tuple[List[float], List[float]]:
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

        highs: List[float] = []
        lows: List[float] = []
        for item in xml_temperatures:
            max_values = extract_temperatures(item, "maximum")
            if max_values:
                highs = max_values
            min_values = extract_temperatures(item, "minimum")
            if min_values:
                lows = min_values
        if len(highs) == days and len(lows) == days:
            return highs, lows
        raise InvalidXMLDataException(
            f"Wrong number of temperatures: max number {len(highs)}, min number {len(lows)}. Expected {days}."
        )


if __name__ == "__main__":  # pragma: no cover
    from pprint import pprint

    weather = Weather()
    pprint(weather.get_weather("39.3286", "-76.6169", days=1))
