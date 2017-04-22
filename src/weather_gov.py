# works for USA only (NDFD regions)

from xml.dom import minidom
import datetime
from urllib.request import urlopen


class Weather(object):
    def __init__(self, settings):
        self.settings = settings

    def get_weather(latitude, longitude, days=1, units='m'):
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
    from iot_calendar import load_settings
    settings = load_settings()
    weather = Weather(settings)
    pprint(weather.get_weather('39.3286', '-76.6169'))

# freezing drizzle
# freezing rain
# snow showers
# blowing snow
# blowing dust
# rain showers
# ice pellets
# frosts
# rain
# hail
# snow
# thunderstorms
# drizzle
# fog
# haze
# smoke

# bkn
# dust
# few
# fg
# fzra
# fzrara
# hi_shwrs
# hi_tsra
# ip
# mist
# mix
# nsurtsra
# ovc
# ra
# ra1
# raip
# rasn
# sct
# shra
# skc
# smoke
# sn
# tsra
# wind
