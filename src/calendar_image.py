import os
import datetime
import matplotlib
from matplotlib.dates import date2num, DateFormatter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from dateutil.tz import tzoffset
from io import BytesIO
import numpy as np
import hashlib
from cached_decorator import cached
import PIL.Image
from collections import namedtuple


IMAGE_CACHED_SECONDS = 60 * 60 * 24 *30
ImageParams = namedtuple('ImageParams', 'dashboard format style xkcd rotate')

weeks = 4

dpi = 100
picture_width = 8 # * dpi = 800  # I cannot remove padding around drawing so I have to manually
picture_height = 6 #* (600 / 614) # * dpi = 600 # ajust image to be exactly 800x600. Not sure if that has good stability.

left_gap = 0.01
pies_height = 3.5 / 6 # vertical proportion between weeks grid and plot above it
pies_top = 1 - pies_height

WEEK_DAYS = 7
pie_row_header_width = (1 / WEEK_DAYS) / 3
pie_width = (1 - pie_row_header_width) / WEEK_DAYS
pie_col_header_height = (pies_height / weeks) / 5
pie_height = (pies_height - pie_col_header_height) / weeks
pie_scale = 0.9

legend_image_sz = 0.2 # size of legend icons in 1 x 1

width_aspect = 1.282 # horizontal scale to fill full width of weeks grid

watch_left = 0
watch_width = 0.3
watch_height = 1 - pies_height
watch_bottom = 1 - watch_height

plot_left = watch_width
plot_width = 1 - watch_width - 0.025 # -0.02 to remove padding - tight layout do not remove it
plot_height = 1 - pies_height - 0.125
plot_bottom = 1 - plot_height - 0.025

last_image = {
}

def draw_pies(grid, weeks=4, empty_image_file_name=None):
    def find_max_total(grid):
        max_total = 0
        for week in range(len(grid)):
            for day in range(len(grid[week])):
                total = sum(grid[week][day]['values'])
                if total > max_total:
                    max_total = total
        return max_total

    def draw_day_headers():
        for day in range(WEEK_DAYS):
            plt.text(
                (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
                weeks * pie_height + 0.5 * pie_col_header_height,
                grid[0][day]['date'].strftime('%A'),
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=12
            )

    def draw_week_headers():
        for week in range(weeks):
            plt.text(
                pie_row_header_width * 0.5,
                (week + 0.5) * pie_height,
                grid[week][0]['date'].strftime('%d\n%b'),
                horizontalalignment='center',
                verticalalignment='center',
                fontsize=14
            )

    def draw_pie(week, day, values):
        radius = sum(values) / max_total * pie_height * pie_scale / 2
        colours = ['C{}'.format(i) for i in range(len(values))]
        explode = [0.007 for i in range(len(values))]
        plt.pie(
            values,
            #shadow=True,
            explode=explode,
            radius=radius,
            colors=colours,
            center=(
                (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
                (week + 0.5) * pie_height
            )
        )

    def draw_empty_pie(week, day):
        image_padding = pie_width / 5
        if grid[week][day]['date'] < tomorrow and empty_image_file_name:
            plt.imshow(
                img,
                extent=((pie_row_header_width + day * pie_width + image_padding) * width_aspect,
                        (pie_row_header_width + (day + 1) * pie_width - image_padding) * width_aspect,
                        week * pie_height + image_padding,
                        (week + 1) * pie_height - image_padding),
                interpolation='bicubic'
            )

    def draw_today(today):
        grid_shift = (today - grid[0][0]['date']).days
        day = grid_shift % WEEK_DAYS
        week = grid_shift // WEEK_DAYS
        plt.gca().add_patch(
            patches.Rectangle(
                ((pie_row_header_width + day * pie_width) * width_aspect, week * pie_height),
                pie_width * width_aspect * 0.98,
                pie_height,
                edgecolor='black',
                fill=False,
                linewidth=2
            )
        )

    max_total = find_max_total(grid)
    if empty_image_file_name:
        img = mpimg.imread(empty_image_file_name)
    today = datetime.datetime.now(grid[0][0]['date'].tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + datetime.timedelta(days=1)
    ax = plt.gcf().add_axes(
        [left_gap, 0, 1, pies_height], # left, bottom, width, height, in fractions of figure width and height
        frameon=False,
        autoscale_on=False,
    )
    plt.axis('off')
    draw_today(today)
    draw_day_headers()
    draw_week_headers()
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]['values']
            if sum(values) <= 0:
                draw_empty_pie(week, day)
            else:
                draw_pie(week, day, values)

    ax.set_ylim(0, pies_height)
    ax.set_xlim(0, width_aspect)
    ax.patch.set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def draw_plot(x, y, labels, rect, legend='inside'):
    ax = plt.axes(rect)
    if len(x) > 0:
        days_on_plot = (x[-1] - x[0]).days
        if days_on_plot < 5 * 30:
            shortFmt = DateFormatter('%b %d')
        elif days_on_plot < 5 * 365:
            shortFmt = DateFormatter('%d')
        else:
            shortFmt = DateFormatter('%Y')
        ax.xaxis.set_major_formatter(shortFmt)
    legend_labels = [label['summary'] for label in labels]
    polies = ax.stackplot(x, y)
    ax.patch.set_visible(False)
    if legend == 'rectangle':
        plt.legend([plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]) for poly in polies], legend_labels)
    elif legend == 'inside':
        #y_sum = np.sum(np.array(y), axis=0)
        #y_max = y_sum.max()
        for region in range(len(labels)):
            if len(y[region]) == 0:
                return
            max_idx, _ = max(enumerate(y[region]), key=lambda item: item[1])
            x_pos = x[max_idx]
            y_pos = y[region][max_idx]
            ax.text(
                x_pos,
                y_pos,
                labels[region]['summary'],
                horizontalalignment='center',
                verticalalignment='top'
            )
            if 'image' in labels[region]:
                legend_text_height = 0.13
                ylim = ax.get_ylim()
                xlim = ax.get_xlim()
                xsz = xlim[1] - xlim[0]
                ysz = ylim[1] - ylim[0]
                x_scale = 1 / plot_height # at the moment I do not understand why 1 and not plot_width
                x_val = (date2num(x_pos) - xlim[0]) / xsz * x_scale
                y_val = (y_pos - ylim[0]) / ysz
                img = mpimg.imread(labels[region]['image'])
                axes = plt.axes([plot_left, plot_bottom, plot_width, plot_height], label='2')
                plt.axis('off')
                axes.patch.set_visible(False)
                axes.set_xticklabels([])
                axes.set_yticklabels([])
                axes.set_ylim((0, 1))
                axes.set_xlim((0, x_scale))
                imgplot = plt.imshow(
                    img,
                    extent=(x_val - legend_image_sz / 2, x_val + legend_image_sz / 2,
                            y_val - legend_image_sz - legend_text_height, y_val - legend_text_height),
                    interpolation='bicubic'
                )
                #imgplot.set_cmap('jet')


def draw_weather(weather, rect):
    ax = plt.axes(rect)
    plt.axis('off')
    ax.patch.set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlim(-0.03, 1.03)
    ax.text(
        0.5,
        1,
        datetime.datetime.now().strftime('%d %B'),
        horizontalalignment='center',
        verticalalignment='top'
    )
    if not weather:
        return
    ax.text(
        0.5,
        0,
        '{} °C … {} °C'.format(round(weather['temp_min'][0], 1), round(weather['temp_max'][0], 1)),
        horizontalalignment='center',
        verticalalignment='bottom'
    )
    img = mpimg.imread(os.path.join(weather['images_folder'], weather['icon'][0] + '.png'))
    plt.imshow(
        img,
        extent=[0.15, 0.85, 0.15, 0.85],
        interpolation='bilinear' #'bicubic'
    )


@cached(
    cache_time_seconds=IMAGE_CACHED_SECONDS,
    print_if_cached='Use stored imaged without rendering (from {time})',
    evaluate_on_day_change=True
)
def draw_calendar(grid, x, y, weather, dashboard, labels, params):
    plt.clf()
    plt.close()
    plt.figure(figsize=(picture_width, picture_height), dpi=dpi, facecolor='white')
    #plt.style.use(style) # that does not apply new style: https://github.com/matplotlib/matplotlib/issues/8348
    with plt.style.context(params.style, after_reset=True):
        if int(params.xkcd):
            plt.xkcd()
        draw_weather(weather, rect=[0, plot_bottom, plot_left * 0.8, plot_height])
        draw_plot(x, y, labels, rect=[plot_left, plot_bottom, plot_width, plot_height])
        draw_pies(
            grid,
            weeks=weeks,
            empty_image_file_name=dashboard['empty_image']
        )
        #plt.tight_layout(pad=0)
        #plt.rcParams['savefig.pad_inches'] = 0
        #plt.rcParams['savefig.jpeg_quality'] = 80
        plt.gcf().canvas.draw()
        bitmap = np.fromstring(plt.gcf().canvas.tostring_rgb(), dtype=np.uint8, sep='') \
            .reshape(plt.gcf().canvas.get_width_height()[::-1] + (3,))
        bitmap = np.rot90(bitmap, k=int(params.rotate) // 90)
        image = PIL.Image.fromarray(bitmap)
        bytes_file = BytesIO()
        image.save(bytes_file, format=params.format)
        # plt.savefig(
        #     bytes_file,
        #     dpi=dpi,
        #     pad_inches=0,
        #     #bbox_inches='tight', # we want exact size specified for the picture, not the actual drawing size
        #     frameon=False,
        #     format=format,
        #     #jpeg_quality=70, # no gain here (117kB vs 113 with 70% jpeg compression quality) so better use loseless png
        #     #cmap='gray',
        # )
        return bytes_file.getvalue()


def test():
    from io import BytesIO
    x = [datetime.datetime(2017, 4, 6, 0, 0), datetime.datetime(2017, 4, 7, 0, 0), datetime.datetime(2017, 4, 8, 0, 0), datetime.datetime(2017, 4, 11, 0, 0), datetime.datetime(2017, 4, 12, 0, 0), datetime.datetime(2017, 4, 13, 0, 0), datetime.datetime(2017, 4, 14, 0, 0), datetime.datetime(2017, 4, 16, 0, 0), datetime.datetime(2017, 4, 17, 0, 0),
         datetime.datetime(2017, 4, 18, 0, 0), datetime.datetime(2017, 4, 19, 0, 0), datetime.datetime(2017, 4, 20, 0, 0), datetime.datetime(2017, 4, 22, 0, 0), datetime.datetime(2017, 4, 23, 0, 0)]
    y = [[0.0, 15.0, 9.0, 0.0, 9.0, 5.0, 6.0, 0.0, 11.0, 9.0, 5.0, 6.0, 0.0, 11.0],
         [15.0, 17.0, 0.0, 20.0, 20.0, 19.0, 30.0, 32.0, 23.0, 20.0, 19.0, 30.0, 32.0, 23.0]]
    grid = [
        [{'date': datetime.datetime(2017, 4, 3, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 4, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 5, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 6, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  15.]}, {'date': datetime.datetime(2017, 4, 7, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 15.,  17.]}, {'date': datetime.datetime(2017, 4, 8, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 9.,  0.]}, {'date': datetime.datetime(2017, 4, 9, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}],
        [{'date': datetime.datetime(2017, 4, 10, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 11, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  20.]}, {'date': datetime.datetime(2017, 4, 12, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  9.,  20.]}, {'date': datetime.datetime(2017, 4, 13, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  5.,  19.]}, {'date': datetime.datetime(2017, 4, 14, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  6.,  30.]}, {'date': datetime.datetime(2017, 4, 15, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 16, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  32.]}],
        [{'date': datetime.datetime(2017, 4, 17, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 11.,  23.]}, {'date': datetime.datetime(2017, 4, 18, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 19, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 20, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 21, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 22, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 23, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}],
        [{'date': datetime.datetime(2017, 4, 24, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 11.,  23.]}, {'date': datetime.datetime(2017, 4, 25, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 26, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 27, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 28, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 29, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 30, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}]
            ]
    dashboard = {
        "summary": "Anna work-out",
        "empty_image": "../amazon-dash-private/images/old-woman.png",
        "images_folder": "../amazon-dash-private/images/"
    }
    labels = [
        {"summary": "Morning work-out", "image": "../amazon-dash-private/images/morning4.png"},
        {"summary": "Physiotherapy", "image": "../amazon-dash-private/images/evening2.png"}
    ]
    weather = {'day': [datetime.datetime(2017, 4, 22, 0, 0),
                       datetime.datetime(2017, 4, 23, 0, 0),
                       datetime.datetime(2017, 4, 24, 0, 0),
                       datetime.datetime(2017, 4, 25, 0, 0)],
               'icon': ['sct', 'ovc', 'hi_shwrs', 'sn'],
               'temp_max': [6.64, 6.38, 4.07, 6.91],
               'temp_min': [-0.58, -2.86, -1.87, -1.91],
               'images_folder': '../amazon-dash-private/images/'}
    t0 = datetime.datetime.now()
    image_data = draw_calendar(grid, x, y, weather, dashboard, labels,
                               ImageParams(
                                   dashboard='',
                                   format='gif',
                                   style='seaborn-talk',
                                   xkcd=1,
                                   rotate=0
                               )
                               )
    t1 = datetime.datetime.now()
    print(t1 - t0)
    image_file = BytesIO(image_data)
    image = PIL.Image.open(image_file)
    image.show()
    # with open('test.png', 'wb') as png_file:
    #     png_file.write(image)
    #plt.show()
    #todo speed it up. too many rescalings as I see from profiling.
    # may be using artists (http://stackoverflow.com/questions/41453902/is-it-possible-to-patch-an-image-in-matplotlib)
    # will reduce number of rescaling?
    # now it looks like matplotlib rescales after each operation


if __name__ == '__main__':
    test()
