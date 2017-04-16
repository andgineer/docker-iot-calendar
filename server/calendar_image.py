import svgwrite
import datetime


def calendar_image_as_svg():
    COLOR = 'black'
    dwg = svgwrite.Drawing(size=('600', '800'))
    dwg.add(dwg.line(start=(0, 0), end=(600, 600), stroke_width=3, stroke=COLOR))
    dwg.add(dwg.line(start=(600, 0), end=(0, 600), stroke_width=3, stroke=COLOR))
    dwg.add(dwg.text(datetime.datetime.now().strftime('%H:%M:%S'), insert=(100, 20), fill=COLOR))
    svgwrite.image.Image('static/img/morning.svg', insert=(0, 0), size=(100,100))
    return dwg.tostring()


if __name__ == '__main__':
    with open('test.svg', 'w') as svg_file:
        svg_file.write(calendar_image_as_svg())
