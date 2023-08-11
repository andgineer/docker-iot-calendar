"""
Draws IoT calendar as bitmap image.

Usage
    draw_calendar(parameters)
    see details in the function description
"""

import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Union, Optional

import matplotlib
try: # !!! that should be before importing pyplot
    import tkinter # check if tkinter is installed
    matplotlib.use('TkAgg') # in MacOS we should have tkinter installed and use it as backend
except ImportError:
    pass # in Docker container (where no tkinter installed) we use default matplotlib backend
from matplotlib.dates import date2num, DateFormatter
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import matplotlib.patches as patches
from dateutil.tz import tzoffset
from io import BytesIO
import numpy as np
from cached_decorator import cached
from cached_image import CachedImage
import PIL.Image
from collections import namedtuple


IMAGE_CACHED_SECONDS = 60 * 60 * 24 *30
ImageParams = namedtuple('ImageParams', 'dashboard format style xkcd rotate')

weeks = 4

dpi = 100
picture_width = 800 // dpi
picture_height = 600 // dpi

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


def get_daily_max(grid: List[List[Dict[str, List[int]]]]) -> int:
    """Maximum sum of 'values' for a day."""
    return max((sum(day['values']) for week in grid for day in week), default=0)


def draw_day_headers(grid: List[List[Dict[str, Any]]]) -> None:
    """Draws the day headers for a grid.

    Args:
    - grid (List[List[Dict[str, Any]]]): A 2D grid [week][day]
    """
    for day in range(WEEK_DAYS):
        plt.text(
            (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
            weeks * pie_height + 0.5 * pie_col_header_height,
            grid[0][day]['date'].strftime('%A'),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=12
        )


def draw_week_headers(grid: List[List[Dict[str, any]]]) -> None:
    """Draw headers for each week on the grid using the date from the first day of each week.

    Args:
    - grid (List[List[Dict[str, Any]]]): A 2D grid [week][day]
    """
    for week in range(weeks):
        plt.text(
            pie_row_header_width * 0.5,
            (week + 0.5) * pie_height,
            grid[week][0]['date'].strftime('%d\n%b'),
            horizontalalignment='center',
            verticalalignment='center',
            fontsize=14
        )


def draw_pie(week: int, day: int, values: List[Union[int, float]], daily_max: Union[int, float]) -> None:
    """Draws a pie chart for a specific day of a week based on the given values.

    Parameters:
    - week (int): The index of the week.
    - day (int): The index of the day within the week.
    - values (List[Union[int, float]]): A list of numerical values for each slice of the pie chart.
    - daily_max (Union[int, float]): The maximum value for the day, used to determine the pie's radius.
    """
    radius = sum(values) / daily_max * pie_height * pie_scale / 2
    colours = [f'C{i}' for i in range(len(values))]
    explode = [0.007 for _ in range(len(values))]
    plt.pie(
        values,
        # shadow=True,
        explode=explode,
        radius=radius,
        colors=colours,
        center=(
            (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
            (week + 0.5) * pie_height
        )
    )


def draw_empty_pie(
        grid: List[List[Dict[str, Union[datetime, List[Dict[str, Any]]]]]],
        image_cache: CachedImage,
        week: int,
        day: int,
        absent_grid_images: Dict[str, str],
        empty_image_file_name: str,
        tomorrow: datetime
) -> None:
    """Draw an empty pie (or use an absent image) for a given week and day on the grid.

    Do not fill cells for a days in the future (after `tomorrow`).

    Args:
    - grid: The grid representing the schedule [week][day]["date"].
    - image_cache: Cache containing the necessary images.
    - week: The week index for which to draw the pie.
    - day: The day index for which to draw the pie.
    - absent_grid_images: Dictionary mapping absent summary to image file names
        - "image_grid" from "absent" array in the settings.
    - empty_image_file_name: Name of the file to use for the empty image.
    - tomorrow: The datetime representing the start of the next day.
    """
    image_padding = pie_width / 5
    if 'absents' in grid[week][day]:
        image = image_cache.by_file_name(absent_grid_images[grid[week][day]['absents'][0]['summary']])
    else:
        image = image_cache.by_file_name(empty_image_file_name)
    if grid[week][day]['date'] < tomorrow:
        plt.imshow(
            image,
            extent=((pie_row_header_width + day * pie_width + image_padding) * width_aspect,
                    (pie_row_header_width + (day + 1) * pie_width - image_padding) * width_aspect,
                    week * pie_height + image_padding,
                    (week + 1) * pie_height - image_padding),
            interpolation='bicubic'
        )


def highlight_today(grid: List[List[Dict[str, Any]]], today: datetime) -> None:
    """Draw a rectangle around the current day in the grid to highlight it.

    Parameters:
    - grid: The grid representing the schedule [week][day]["date"].
    - today: A datetime object representing the current day.
    """
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


def draw_pies(grid: List[List[Dict[str, Any]]],
              image_cache: CachedImage,
              weeks: int = 4,
              absent_grid_images: Optional[Dict[str, str]] = None,
              empty_image_file_name: Optional[str] = None) -> None:
    """
    Draws pie charts or images for each day in the provided grid based on the data provided.

    Parameters:
    - grid: The grid representing the schedule [week][day]["date"]/["values"].
    - image_cache: A cache object used to fetch images.
    - weeks: Number of weeks to consider. Default is 4.
    - absent_grid_images: Dictionary mapping absent summary to image file names
        - "image_grid" from "absent" array in the settings. Optional.
    - empty_image_file_name: File name of the image to use when there's no data. Optional.
    """
    daily_max = get_daily_max(grid)
    today = datetime.now(grid[0][0]['date'].tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + timedelta(days=1)
    ax = plt.gcf().add_axes(
        [left_gap, 0, 1, pies_height],  # left, bottom, width, height, in fractions of figure width and height
        frameon=False,
        autoscale_on=False,
    )
    plt.axis('off')
    highlight_today(grid, today)
    draw_day_headers(grid)
    draw_week_headers(grid)
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]['values']
            if sum(values) <= 0:
                draw_empty_pie(grid, image_cache, week, day, absent_grid_images, empty_image_file_name, tomorrow)
            else:
                draw_pie(week, day, values, daily_max)

    ax.set_ylim(0, pies_height)
    ax.set_xlim(0, width_aspect)
    ax.patch.set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])

def draw_weather(weather: Optional[Dict[str, Union[str, List[float]]]],
                 rect: List[float],
                 image_cache: CachedImage) -> None:
    """
    Renders the weather data onto a specified rectangle using matplotlib.

    Parameters:
    - weather (Optional[Dict[str, Union[str, List[float]]]]):
        A dictionary containing weather data.
        It should have the following keys:
        - 'temp_min': List containing minimum temperature (only first element is used).
        - 'temp_max': List containing maximum temperature (only first element is used).
        - 'images_folder': Path to the folder containing weather icons.
        - 'icon': List containing the name of the icon file (without extension, only first element is used).
        If weather is None, it renders the date only.

    - rect (List[float]):
        A list of four float numbers specifying the [left, bottom, width, height]
        of the rectangle where the weather data should be rendered.

    - image_cache (CachedImage):
        An instance of CachedImage to fetch images by file name.
    """
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
        datetime.now().strftime('%d %B'),
        horizontalalignment='center',
        verticalalignment='top'
    )
    if not weather:
        return
    ax.text(
        0.5,
        0,
        f"{round(weather['temp_min'][0], 1)} °C … {round(weather['temp_max'][0], 1)} °C",
        horizontalalignment='center',
        verticalalignment='bottom',
    )
    plt.imshow(
        image_cache.by_file_name(os.path.join(weather['images_folder'], weather['icon'][0] + '.png')),
        extent=[0.15, 0.85, 0.15, 0.85],
        interpolation='bilinear' #'bicubic'
    )


@cached(
    cache_time_seconds=IMAGE_CACHED_SECONDS,
    print_if_cached='Use stored imaged without rendering (from {time})',
    evaluate_on_day_change=True
)
def draw_calendar(grid, x, y, weather, dashboard, labels, absent_labels, params):
    """
    Draws IoT calendar as image, optimized for Amazon Kindle (600 x 800).
    To prepare data see functions in calendar_data.py

    :param grid:
        grid[weeks][days]
    :param x:
    :param y:
        y[event_list][x]
    :param weather:
        {'temp_min': [], 'temp_max': [], 'icon': [], 'day': []}
    :param dashboard: {
        'summary': summary,
        'empty_image': full_path_to_empty_cell_image,
        'absent': array of absence images descriptions}
    :param labels: [
            {'summary': label_summary, 'image': full_path_to_image_to_display_on_plot}
        ]
    :param absent_labels: [
        {'summary': event_name_in_calendar, 'image_grid': full_path_to_cell_image,
          'image_plot': full_path_to_plot_image}
    :param params:
        see ImageParams
    :return:
        image data in specified (in params) format (png, gif etc)
    """
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
        ax.xaxis.set_major_locator(plt.MaxNLocator(6))
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
                    axes = plt.axes([plot_left, plot_bottom, plot_width, plot_height], label='2')
                    plt.axis('off')
                    axes.patch.set_visible(False)
                    axes.set_xticklabels([])
                    axes.set_yticklabels([])
                    axes.set_ylim((0, 1))
                    axes.set_xlim((0, x_scale))
                    plt.imshow(
                        image_cache.by_file_name(labels[region]['image']),
                        extent=(x_val - legend_image_sz / 2, x_val + legend_image_sz / 2,
                                y_val - legend_image_sz - legend_text_height, y_val - legend_text_height),
                        interpolation='bicubic'
                    )

    plt.clf()
    plt.figure(figsize=(picture_width, picture_height), dpi=dpi, facecolor='white')
    absent_grid_images = {absent['summary'] : absent['image_grid'] for absent in absent_labels}
    image_cache = CachedImage()
    plt.rcParams.update(plt.rcParamsDefault)
    with plt.style.context(params.style, after_reset=True):
        if int(params.xkcd):
            plt.xkcd()
        draw_weather(weather, rect=[0, plot_bottom, plot_left * 0.8, plot_height], image_cache=image_cache)
        draw_plot(x, y, labels, rect=[plot_left, plot_bottom, plot_width, plot_height])
        draw_pies(
            grid,
            image_cache=image_cache,
            weeks=weeks,
            absent_grid_images=absent_grid_images,
            empty_image_file_name=dashboard['empty_image']
        )
        plt.gcf().canvas.draw()
        bitmap = np.fromstring(plt.gcf().canvas.tostring_rgb(), dtype=np.uint8, sep='') \
            .reshape(plt.gcf().canvas.get_width_height()[::-1] + (3,))
        bitmap = np.rot90(bitmap, k=int(params.rotate) // 90)
        image = PIL.Image.fromarray(bitmap)
        bytes_file = BytesIO()
        image.save(bytes_file, format=params.format)
        return bytes_file.getvalue()


def check():  # pragma: no cover
    """Debugging function.

    To create the file with parameters for the check(), add the following code to the draw_calendar()

        call_params = dict(grid=grid, x=x, y=y, weather=weather, dashboard=dashboard, labels=labels,
            absent_labels=absent_labels, params=params)
        import json
        json.dump(call_params, open('draw_calendar_params.json', 'w'), default=str)
    """
    import json
    import dateutil
    call_params = json.load(open('tests/resources/draw_calendar_params_2.json', 'r'))
    for row in call_params['grid']:
        for col in row:
            col['date'] = dateutil.parser.parse(col['date'])
    for i, day in enumerate(call_params['x']):
        call_params['x'][i] = dateutil.parser.parse(call_params['x'][i])
    t0 = datetime.now()
    image_data = draw_calendar(
        call_params['grid'],
        call_params['x'],
        call_params['y'],
        call_params['weather'],
        call_params['dashboard'],
        call_params['labels'],
        call_params['absent_labels'],
        ImageParams(*call_params['params'])
    )
    t1 = datetime.now()
    print(t1 - t0)
    image_file = BytesIO(image_data)
    image = PIL.Image.open(image_file)
    image.show()


if __name__ == '__main__':
    check()
