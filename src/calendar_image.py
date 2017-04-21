import os
import datetime
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from dateutil.tz import tzoffset
from io import BytesIO

weeks = 4

dpi = 100
picture_width = 8 * (800 / 821) # * dpi = 800  # I cannot remove padding around drawing so I have to manually
picture_height = 6 * (600 / 614) # * dpi = 600 # ajust image to be exactly 800x600. Not sure if that has good stability.

left_gap = 0.01
pies_height = 3.5 / 6 # vertical proportion between weeks grid and plot above it
pies_top = 1 - pies_height

WEEK_DAYS = 7
pie_row_header_width = (1 / WEEK_DAYS) / 3
pie_width = (1 - pie_row_header_width) / WEEK_DAYS
pie_col_header_height = (pies_height / weeks) / 5
pie_height = (pies_height - pie_col_header_height) / weeks
pie_scale = 0.9

grid_aspect = 1.345 # horizontal scale to fill full width of weeks grid

watch_left = 0
watch_width = 0.3
watch_height = 1 - pies_height
watch_bottom = 1 - watch_height

plot_left = watch_width
plot_width = 1 - watch_width
plot_height = 1 - pies_height - 0.1
plot_bottom = 1 - plot_height


def draw_plot(axes, x, y, labels, legend='rectangle'):
    legend_labels = [label['summary'] for label in labels]
    polies = axes.stackplot(x, y)
    axes.patch.set_visible(False)
    if legend == 'rectangle':
        plt.legend([plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]) for poly in polies], legend_labels)
    elif legend == 'inside':
        #loc = y1.argmax()
        #ax.text(loc, y1[loc]*0.25, areaLabels[0])
        pass


def draw_pies(figure, grid, weeks=4, empty_image_file_name=None):
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
                (pie_row_header_width + (day + 0.5) * pie_width) * grid_aspect,
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
            center=((pie_row_header_width + (day + 0.5) * pie_width) * grid_aspect, (week + 0.5) * pie_height)
        )

    def draw_empty_pie(week, day):
        image_padding = pie_width / 5
        if grid[week][day]['date'] < tomorrow and empty_image_file_name:
            plt.imshow(
                img,
                extent=((pie_row_header_width + day * pie_width + image_padding) * grid_aspect,
                        (pie_row_header_width + (day + 1) * pie_width - image_padding) * grid_aspect,
                        week * pie_height + image_padding,
                        (week + 1) * pie_height - image_padding))

    max_total = find_max_total(grid)
    if empty_image_file_name:
        img = mpimg.imread(empty_image_file_name)
    tomorrow = datetime.datetime.now(grid[0][0]['date'].tzinfo).replace(hour=0, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
    axs = []
    ax = figure.add_axes(
        [left_gap, 0, 1, pies_height], # left, bottom, width, height, in fractions of figure width and height
        frameon=False,
        autoscale_on=False,
        ylim=(0, pies_height),
        xlim=(0, grid_aspect)
    )
    plt.axis('off')
    axs.append(ax)
    draw_day_headers()
    draw_week_headers()
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]['values']
            if sum(values) <= 0:
                draw_empty_pie(week, day)
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]['values']
            if sum(values) > 0:
                draw_pie(week, day, values)
    ax.set_ylim(0, pies_height)
    ax.set_xlim(0, grid_aspect)
    for ax in axs:
        ax.patch.set_visible(False)
        ax.set_xticklabels([])
        ax.set_yticklabels([])


def draw_calendar(grid, x, y, dashboard, labels, xkcd=True, style='grayscale'):
    if xkcd:
        plt.xkcd()
    figure = plt.figure(figsize=(picture_width, picture_height), dpi=dpi, facecolor='white')
    plt.style.use(style)
    draw_plot(
        plt.axes([plot_left, plot_bottom, plot_width, plot_height]),
        x, y,
        labels
    )
    draw_pies(
        figure,
        grid,
        weeks=weeks,
        empty_image_file_name=os.path.join(dashboard['images_folder'], dashboard['empty_image'])
    )
    bytes_file = BytesIO()
    plt.savefig(bytes_file, dpi=dpi, pad_inches=0, bbox_inches='tight') # cmap='gray'
    return bytes_file.getvalue()


def test():
    x = [datetime.datetime(2017, 4, 6, 0, 0), datetime.datetime(2017, 4, 7, 0, 0), datetime.datetime(2017, 4, 8, 0, 0), datetime.datetime(2017, 4, 11, 0, 0), datetime.datetime(2017, 4, 12, 0, 0), datetime.datetime(2017, 4, 13, 0, 0), datetime.datetime(2017, 4, 14, 0, 0), datetime.datetime(2017, 4, 16, 0, 0), datetime.datetime(2017, 4, 17, 0, 0)]
    y = [[0.0, 15.0, 9.0, 0.0, 9.0, 5.0, 6.0, 0.0, 11.0], [15.0, 17.0, 0.0, 20.0, 20.0, 19.0, 30.0, 32.0, 23.0]]
    grid = [[{'date': datetime.datetime(2017, 3, 27, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 3, 28, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 3, 29, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 3, 30, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 3, 31, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 1, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 2, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}], [{'date': datetime.datetime(2017, 4, 3, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 4, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 5, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 6, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  15.]}, {'date': datetime.datetime(2017, 4, 7, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 15.,  17.]}, {'date': datetime.datetime(2017, 4, 8, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 9.,  0.]}, {'date': datetime.datetime(2017, 4, 9, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}], [{'date': datetime.datetime(2017, 4, 10, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 11, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  20.]}, {'date': datetime.datetime(2017, 4, 12, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  9.,  20.]}, {'date': datetime.datetime(2017, 4, 13, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  5.,  19.]}, {'date': datetime.datetime(2017, 4, 14, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  6.,  30.]}, {'date': datetime.datetime(2017, 4, 15, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 16, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [  0.,  32.]}], [{'date': datetime.datetime(2017, 4, 17, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 11.,  23.]}, {'date': datetime.datetime(2017, 4, 18, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 19, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 20, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 21, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 22, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}, {'date': datetime.datetime(2017, 4, 23, 0, 0, tzinfo=tzoffset(None, 10800)), 'values': [ 0.,  0.]}]]
    dashboard = {
        "summary": "Anna work-out",
        "empty_image": "old-woman.png",
        "images_folder": "../amazon-dash-private/images/"
    }
    labels = [
        {"summary": "Morning work-out", "image": "morning.png"},
        {"summary": "Physiotherapy", "image": "evening.png"}
    ]
    image = draw_calendar(grid, x, y, dashboard, labels, style='seaborn-talk')
    with open('test.png', 'wb') as png_file:
        png_file.write(image)
    print('{}{}{}'.format(pie_height, pie_width, pie_height / pie_width))
    plt.show()


if __name__ == '__main__':
    test()
