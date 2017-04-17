import svgwrite
import datetime
from dateutil.tz import tzoffset


def calendar_image_as_svg():
    COLOR = 'black'
    dwg = svgwrite.Drawing(size=('600', '800'))
    dwg.add(dwg.line(start=(0, 0), end=(600, 600), stroke_width=3, stroke=COLOR))
    dwg.add(dwg.line(start=(600, 0), end=(0, 600), stroke_width=3, stroke=COLOR))
    dwg.add(dwg.text(datetime.datetime.now().strftime('%H:%M:%S'), insert=(100, 20), fill=COLOR))
    svgwrite.image.Image('static/img/morning.svg', insert=(0, 0), size=(100,100))
    return dwg.tostring()

def test():
    events = [
         {'end': datetime.datetime(2017, 4, 6, 20, 17, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 6, 20, 2, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 7, 8, 17, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 7, 8, 2, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 7, 19, 12, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 7, 18, 55, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 8, 11, 11, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 8, 11, 2, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 11, 19, 53, 19, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 11, 19, 33, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 12, 8, 30, 11, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 12, 8, 20, 50, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 12, 20, 39, 3, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 12, 20, 18, 29, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 13, 8, 19, 22, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 13, 8, 13, 24, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 13, 20, 23, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 13, 20, 3, 5, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 14, 8, 22, 30, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 14, 8, 15, 39, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 14, 17, 26, 47, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 14, 16, 55, 56, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 16, 18, 20, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 16, 17, 48, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 17, 8, 27, 43, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 17, 8, 16, 35, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'},
         {'end': datetime.datetime(2017, 4, 17, 17, 51, 35, tzinfo=tzoffset(None, 10800)),
          'start': datetime.datetime(2017, 4, 17, 17, 28, 31, tzinfo=tzoffset(None, 10800)),
          'summary': '#white'}
         ]


if __name__ == '__main__':
    with open('test.svg', 'w') as svg_file:
        svg_file.write(calendar_image_as_svg())
