import cairosvg
import io


def svg_to_png(svg):
    in_mem_file = io.BytesIO()
    cairosvg.svg2png(bytestring=svg, write_to=in_mem_file)
    return in_mem_file.getvalue()


def test():
    svg = '''<?xml version="1.0" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN"
                "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="5cm" height="4cm" version="1.1"
     xmlns="http://www.w3.org/2000/svg">
    <desc>Four separate rectangles
    </desc>
    <rect x="0.5cm" y="0.5cm" width="2cm" height="1cm"/>
    <rect x="0.5cm" y="2cm" width="1cm" height="1.5cm"/>
    <rect x="3cm" y="0.5cm" width="1.5cm" height="2cm"/>
    <rect x="3.5cm" y="3cm" width="1cm" height="0.5cm"/>

    <!-- Show outline of canvas using 'rect' element -->
    <rect x=".01cm" y=".01cm" width="4.98cm" height="3.98cm"
          fill="none" stroke="blue" stroke-width=".02cm" />
</svg>'''
    with open('output.png', 'wb') as png_file:
        png_file.write(svg_to_png(svg))


if __name__ == '__main__':
    test()

