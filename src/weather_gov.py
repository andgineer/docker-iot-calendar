"""
 Loads weather from weather.gov.
 Works for USA only (NDFD regions).

 Usage:
    Weather().get_weather(latitude, longitude)

"""

from xml.dom import minidom
import datetime
from urllib.request import urlopen


class Weather(object):

    def get_weather(self, latitude, longitude, days=1, units='m'):
        """
        :param latitude:
        :param longitude:
        :param days:
        :param units: m - metric, e - USA
        :return:
         {'temp_min': [], 'temp_max': [], 'icon': [], 'day': []}
         or None if no key or load error
        """

        weather_xml = urlopen(
            'http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?'
            'whichClient=NDFDgenByDay&lat={latitude}&lon={longitude}'
            '&format=24+hourly&numDays={days}&Unit={units}'.format(
                latitude=latitude,
                longitude=longitude,
                days=days,
                units=units
            )).read()
        dom = minidom.parseString(weather_xml)
        error = dom.getElementsByTagName('error')
        if error:
            print(weather_xml)
            return None

        # Parse temperatures
        xml_temperatures = dom.getElementsByTagName('temperature')
        highs = [None] * days
        lows = [None] * days
        for item in xml_temperatures:
            if item.getAttribute('type') == 'maximum':
                values = item.getElementsByTagName('value')
                for i in range(len(values)):
                    highs[i] = int(values[i].firstChild.nodeValue)
            if item.getAttribute('type') == 'minimum':
                values = item.getElementsByTagName('value')
                for i in range(len(values)):
                    lows[i] = int(values[i].firstChild.nodeValue)

        xml_icons = dom.getElementsByTagName('icon-link')
        icons = [None] * days
        for i in range(len(xml_icons)):
            icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')

        xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
        day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')

        return {
            'temp_min': highs,
            'temp_max': lows,
            'icon': icons,
            'day': [day_one]
        }


if __name__ == '__main__':
    from pprint import pprint
    weather = Weather()
    pprint(weather.get_weather('39.3286', '-76.6169'))

