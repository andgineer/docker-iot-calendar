#import svgwrite
import datetime
from dateutil.tz import tzoffset
import matplotlib.pyplot as plt
import matplotlib.image as mpimg

# def calendar_image_as_svg():
#     COLOR = 'black'
#     dwg = svgwrite.Drawing(size=('600', '800'))
#     dwg.add(dwg.line(start=(0, 0), end=(600, 600), stroke_width=3, stroke=COLOR))
#     dwg.add(dwg.line(start=(600, 0), end=(0, 600), stroke_width=3, stroke=COLOR))
#     dwg.add(dwg.text(datetime.datetime.now().strftime('%H:%M:%S'), insert=(100, 20), fill=COLOR))
#     svgwrite.image.Image('static/img/morning.svg', insert=(0, 0), size=(100,100))
#     return dwg.tostring()

explode = (0.1, 0.05)

weeks = 4
days = 7

dpi = 100
picture_width = 8 # * dpi = 800
picture_height = 6 # * dpi = 600

pies_height = 3.5 / 6
pies_top = 1 - pies_height

pie_row_header_width = (1 / days) / 3
pie_width = (1 - pie_row_header_width) / days
pie_col_header_height = (pies_height / weeks) / 5
pie_height = (pies_height - pie_col_header_height) / weeks

image_padding = pie_width / 5

watch_left = 0
watch_width = 0.3
watch_height = 1 - pies_height
watch_bottom = 1 - watch_height

plot_left = watch_width
plot_width = 1 - watch_width
plot_height = 1 - pies_height - 0.1
plot_bottom = 1 - plot_height


def draw_plot(axes, x, y, legend_labels):
    polys = axes.stackplot(x, y)
    axes.patch.set_visible(False)
    legendProxies = []
    for poly in polys:
        legendProxies.append(plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]))
    plt.legend(legendProxies, legend_labels)
    #plt.legend([s, s2],
    #       ['Scatters 1', 'Scatters 2'],
    #       #handler_map={s: custom_handler, s2: custom_handler},
    #       labelspacing=2,
    #       frameon=False)


def draw_pies(grid):
    max_total = 0
    for week in range(weeks):
        for day in range(days):
            total = sum(fracs[week][day])
            if total > max_total:
                max_total = total

    img = mpimg.imread('old-woman.png')
    tomorrow = datetime.datetime.now(grid[0][0]['date'].tzinfo).replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    axs = []
    for row in range(weeks + 1):
        if row == 0:
            for day in range(days):
                axs.append(plt.axes([pie_row_header_width + day * pie_width , weeks * pie_height, pie_width, pie_col_header_height], facecolor='white'))
                plt.text(
                    0.5, 0.5,
                    grid[0][day]['date'].strftime('%A'),
                    horizontalalignment='center',
                    verticalalignment='center',
                    fontsize=12
                )
                plt.axis('off')
        else:
            for col in range(days + 1):
                if col == 0:
                    axs.append(plt.axes([0, (row - 1) * pie_height, pie_row_header_width, pie_height], facecolor='white'))
                    plt.text(
                        0.5, 0.5,
                        grid[row - 1][0]['date'].strftime('%d\n%b'),
                        horizontalalignment='center',
                        verticalalignment='center',
                        fontsize=14
                    )
                    plt.axis('off')
                else:
                    values = grid[row - 1][col - 1]['values']
                    total = sum(values)

                    if total > 0:
                        axs.append(plt.axes([pie_row_header_width + (col - 1) * pie_width, (row - 1) * pie_height, pie_width, pie_height], facecolor='white'))
                        plt.axis('off')
                        radius = total / max_total
                        plt.pie(values, shadow=True, explode=explode, radius=radius)
                    else:
                        axs.append(plt.axes([pie_row_header_width + (col - 1) * pie_width + image_padding,
                                             (row - 1) * pie_height + image_padding,
                                             pie_width - image_padding,
                                             pie_height - image_padding], facecolor='white'))
                        plt.axis('off')
                        if grid[row - 1][col - 1]['date'] < tomorrow:
                            plt.imshow(img, aspect=1)

    for ax in axs:
        ax.patch.set_visible(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])


if __name__ == '__main__':
    plt.figure(figsize=(picture_width, picture_height), dpi=dpi)
    plt.style.use('grayscale')

    draw_plot(
        plt.axes([plot_left, plot_bottom, plot_width, plot_height], facecolor='white'),
        x, y,
        ['morning', 'evening'])

    draw_pies(grid)

    plt.savefig('myfig.png', dpi=dpi, cmap='gray', pad_inches=0, bbox_inches='tight')

    plt.show()
    # with open('test.svg', 'w') as svg_file:
    #     svg_file.write(calendar_image_as_svg())
