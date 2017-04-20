from xml.dom import minidom
import datetime
import codecs
from urllib.request import urlopen

#
# Geographic location
#

latitude = 39.3286
longitude = -76.6169

#
# Download and parse weather data
#

# Fetch data (change lat and lon to desired location)
weather_xml = urlopen('http://graphical.weather.gov/xml/SOAP_server/ndfdSOAPclientByDay.php?whichClient=NDFDgenByDay&lat=' + str(latitude) + '&lon=' + str(longitude) + '&format=24+hourly&numDays=4&Unit=e').read()
dom = minidom.parseString(weather_xml)

# Parse temperatures
xml_temperatures = dom.getElementsByTagName('temperature')
highs = [None]*4
lows = [None]*4
for item in xml_temperatures:
    if item.getAttribute('type') == 'maximum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            highs[i] = int(values[i].firstChild.nodeValue)
    if item.getAttribute('type') == 'minimum':
        values = item.getElementsByTagName('value')
        for i in range(len(values)):
            lows[i] = int(values[i].firstChild.nodeValue)

# Parse icons
xml_icons = dom.getElementsByTagName('icon-link')
icons = [None]*4
for i in range(len(xml_icons)):
    icons[i] = xml_icons[i].firstChild.nodeValue.split('/')[-1].split('.')[0].rstrip('0123456789')

xml_day_one = dom.getElementsByTagName('start-valid-time')[0].firstChild.nodeValue[0:10]
day_one = datetime.datetime.strptime(xml_day_one, '%Y-%m-%d')

#output = codecs.open('weather-face.svg', 'r', encoding='utf-8').read()

#codecs.open('weather-script-output.svg', 'w', encoding='utf-8').write(output)

# <xsd:enumeration value="freezing drizzle"/>
# <xsd:enumeration value="freezing rain"/>
# <xsd:enumeration value="snow showers"/>
# <xsd:enumeration value="blowing snow"/>
# <xsd:enumeration value="blowing dust"/>
# <xsd:enumeration value="rain showers"/>
# <xsd:enumeration value="ice pellets"/>
# <xsd:enumeration value="frosts"/>
# <xsd:enumeration value="rain"/>
# <xsd:enumeration value="hail"/>
# <xsd:enumeration value="snow"/>
# <xsd:enumeration value="thunderstorms"/>
# <xsd:enumeration value="drizzle"/>
# <xsd:enumeration value="fog"/>
# <xsd:enumeration value="haze"/>
# <xsd:enumeration value="smoke"/>
