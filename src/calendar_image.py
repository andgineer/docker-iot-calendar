#import svgwrite
import datetime
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


class ImageHandler(HandlerBase):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize,
                       trans):

        # enlarge the image by these margins
        sx, sy = self.image_stretch

        # create a bounding box to house the image
        bb = Bbox.from_bounds(xdescent - sx,
                              ydescent - sy,
                              width + sx,
                              height + sy)

        tbb = TransformedBbox(bb, trans)
        image = BboxImage(tbb)
        image.set_data(self.image_data)

        self.update_prop(image, orig_handle, legend)

        return [image]

    def set_image(self, image_path, image_stretch=(0, 0)):
        if os.path.exists(image_path):
            self.image_data = read_png(image_path)
        self.image_stretch = image_stretch

from matplotlib.legend_handler import HandlerPatch
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


class HandlerRectangle(HandlerPatch):
    def create_artists(self, legend, orig_handle,
                       xdescent, ydescent, width, height, fontsize, trans):
        bb = Bbox.from_bounds(xdescent - 0,
                              ydescent - 20,
                              width + 0,
                              height + 8)

        tbb = TransformedBbox(bb, trans)
        image = BboxImage(tbb)
        image.set_data(self.image_data)

        self.update_prop(image, orig_handle, legend)
        image.set_transform(trans)
        return [image]

    def set_image(self, image_path, image_stretch=(0, 0)):
        if os.path.exists(image_path):
            self.image_data = read_png(image_path)
        self.image_stretch = image_stretch

def draw_plot(axes, x, y, legend_labels, legend='rectangle'):
    polies = axes.stackplot(x, y)
    axes.patch.set_visible(False)
    if legend == 'rectangle':
        plt.legend([plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]) for poly in polies], legend_labels)
    elif legend == 'icons':
        legend_proxies = []
        handler_map = {}
        for poly in polies:
            patch = mpatches.Rectangle((0, 0), 0.1, 0.1, facecolor=poly.get_facecolor()[0])
            legend_proxies.append(patch)
            image_handler = HandlerRectangle() #ImageHandler()
            image_handler.set_image(image_path='old-woman.png', image_stretch=(0, 16))
            handler_map[poly] = image_handler
        plt.legend(
            legend_proxies,
            legend_labels,
            handleheight=3,
            handlelength=4,
            #handles=[custom_handler],
            #handler_map={mpatches.Rectangle: image_handler},
            handler_map=handler_map, #{s: custom_handler, s2: custom_handler},
            labelspacing=1,
            frameon=True
        )
    elif legend == 'inside':
        #loc = y1.argmax()
        #ax.text(loc, y1[loc]*0.25, areaLabels[0])
        pass

def draw_pies(grid, weeks=4, empty_image_file_name=None):
    def find_max_total(grid):
        max_total = 0
        for week in range(len(grid)):
            for day in range(len(grid[week])):
                total = sum(grid[week][day]['values'])
                if total > max_total:
                    max_total = total
        return max_total

    def draw_day_header(day):
        axs.append(
            plt.axes([
                pie_row_header_width + day * pie_width ,
                weeks * pie_height,
                pie_width,
                pie_col_header_height
            ],
                facecolor='white'))
        plt.text(
            0.5, 0.5,
            grid[0][day]['date'].strftime('%A'),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12
        )
        plt.axis('off')

    def draw_week_header(week):
        axs.append(
            plt.axes([
                0,
                week * pie_height,
                pie_row_header_width,
                pie_height
            ],
                facecolor='white'))
        plt.text(
            0.5, 0.5,
            grid[week][0]['date'].strftime('%d\n%b'),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=14
        )
        plt.axis('off')

    def draw_pie(week, day, values):
        axs.append(
            plt.axes([
                pie_row_header_width + day * pie_width,
                week * pie_height,
                pie_width,
                pie_height
            ],
                facecolor='white'))
        plt.axis('off')
        radius = sum(values) / max_total
        plt.pie(values, shadow=True, explode=explode, radius=radius)

    def draw_empty_pie(week, day):
        axs.append(
            plt.axes([
                pie_row_header_width + day * pie_width + image_padding,
                week * pie_height + image_padding,
                pie_width - image_padding * 2,
                pie_height - image_padding * 2
            ],
                facecolor='white'
            )
        )
        plt.axis('off')
        if grid[week][day]['date'] < tomorrow and empty_image_file_name:
            plt.imshow(img, aspect=1)

    max_total = find_max_total(grid)
    if empty_image_file_name:
        img = mpimg.imread(empty_image_file_name)
    tomorrow = datetime.datetime.now(grid[0][0]['date'].tzinfo).replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    axs = []
    for day in range(len(grid[0])):
        draw_day_header(day)
    for week in range(weeks):
        draw_week_header(week)
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]['values']
            if sum(values) > 0:
                draw_pie(week, day, values)
            else:
                draw_empty_pie(week, day)
    for ax in axs:
        ax.patch.set_visible(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])


if __name__ == '__main__':
    plt.figure(figsize=(picture_width, picture_height), dpi=dpi)
    plt.style.use('grayscale')

    draw_plot(
        plt.axes([plot_left, plot_bottom, plot_width, plot_height]),
        x, y, ['morning', 'evening'])

    draw_pies(grid, weeks=weeks, empty_image_file_name='old-woman.png')

    plt.savefig('myfig.png', dpi=dpi, cmap='gray', pad_inches=0, bbox_inches='tight')

    plt.show()
    # with open('test.svg', 'w') as svg_file:
    #     svg_file.write(calendar_image_as_svg())
