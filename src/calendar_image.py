"""Draw IoT calendar as bitmap image.

Usage
    draw_calendar(parameters)
    see details in the function description
"""


import contextlib
import io
import os
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

import matplotlib
import matplotlib.font_manager

from models import WeatherData, WeatherLabel

# !!! that should be before importing pyplot
with contextlib.suppress(ImportError):
    import tkinter  # noqa: F401  # pylint: disable=unused-import  # check if tkinter is installed

    matplotlib.use("TkAgg")  # in MacOS we should have tkinter installed and use it as backend

from collections import namedtuple
from io import BytesIO

import matplotlib.pyplot as plt  # pylint: disable=ungrouped-imports
import numpy as np
import PIL.Image
from matplotlib import patches
from matplotlib.axes import Axes
from matplotlib.dates import DateFormatter, date2num

from cached_decorator import cached
from image_loader import ImageLoader

matplotlib.font_manager._load_fontmanager(try_read_cache=False)

IMAGE_CACHED_SECONDS = 60 * 60 * 24 * 30
ImageParams = namedtuple("ImageParams", "dashboard format style xkcd rotate")

weeks = 4

dpi = 100
picture_width = 800 // dpi
picture_height = 600 // dpi

left_gap = 0.01
pies_height = 3.5 / 6  # vertical proportion between weeks grid and plot above it
pies_top = 1 - pies_height

WEEK_DAYS = 7
pie_row_header_width = (1 / WEEK_DAYS) / 3
pie_width = (1 - pie_row_header_width) / WEEK_DAYS
pie_col_header_height = (pies_height / weeks) / 5
pie_height = (pies_height - pie_col_header_height) / weeks
pie_scale = 0.9

legend_image_sz = 0.2  # size of legend icons in 1 x 1

width_aspect = 1.282  # horizontal scale to fill full width of weeks grid

watch_left = 0
watch_width = 0.3
watch_height = 1 - pies_height
watch_bottom = 1 - watch_height

plot_left = watch_width
plot_width = 1 - watch_width - 0.025  # -0.02 to remove padding - tight layout do not remove it
plot_height = 1 - pies_height - 0.125
plot_bottom = 1 - plot_height - 0.025


def get_daily_max(grid: List[List[Dict[str, List[int]]]]) -> int:
    """Maximum sum of 'values' for a day."""
    return max((sum(day["values"]) for week in grid for day in week), default=0)


def draw_day_headers(grid: List[List[Dict[str, Any]]]) -> None:
    """Draws the day headers for a grid.

    :param grid: A 2D grid [week][day].
    :return: None
    """
    for day in range(WEEK_DAYS):
        plt.text(
            (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
            weeks * pie_height + 0.5 * pie_col_header_height,
            grid[0][day]["date"].strftime("%A"),
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=12,
        )


def draw_week_headers(grid: List[List[Dict[str, Any]]]) -> None:
    """Draw headers for each week on the grid using the date from the first day of each week.

    :param grid: A 2D grid [week][day].
    :return: None
    """
    for week in range(weeks):
        week_starts_at = grid[week][0]["date"]
        if not isinstance(week_starts_at, datetime):
            raise TypeError(
                f"Expected datetime.datetime, got {type(week_starts_at)} instead: {week_starts_at}"
            )
        plt.text(
            pie_row_header_width * 0.5,
            (week + 0.5) * pie_height,
            week_starts_at.strftime("%d\n%b"),
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=14,
        )


def draw_pie(
    week: int, day: int, values: List[Union[int, float]], daily_max: Union[int, float]
) -> None:
    """Draws a pie chart for a specific day of a week based on the given values.

    :param week: The index of the week.
    :param day: The index of the day within the week.
    :param values: A list of numerical values for each slice of the pie chart.
    :param daily_max: The maximum value for the day, used to determine the pie's radius.
    :return: None
    """
    radius = sum(values) / daily_max * pie_height * pie_scale / 2
    colours = [f"C{i}" for i in range(len(values))]
    explode = [0.007 for _ in range(len(values))]
    plt.pie(
        values,
        # shadow=True,
        explode=explode,
        radius=radius,
        colors=colours,
        center=(
            (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
            (week + 0.5) * pie_height,
        ),
    )


def draw_empty_pie(
    grid: List[List[Dict[str, Union[datetime, List[Dict[str, Any]]]]]],
    image_loader: ImageLoader,
    week: int,
    day: int,
    absent_grid_images: Dict[str, str],
    empty_image_file_name: str,
    tomorrow: datetime,
) -> None:
    """Draw an empty pie (or use an absent image) for a given week and day on the grid.

    Do not fill cells for a days in the future (after `tomorrow`).

    :param grid: The grid representing the schedule with structure [week][day]["date"].
    :param image_loader: Image loader.
    :param week: The week index for which to draw the pie.
    :param day: The day index for which to draw the pie.
    :param absent_grid_images: Dictionary mapping absent summary to image file names.
                               "image_grid" from the "absent" array in the settings.
    :param empty_image_file_name: Name of the file to use for the empty image.
    :param tomorrow: The datetime representing the start of the next day.
    :return: None
    """
    week_starts_at = grid[week][day]["date"]
    if not isinstance(week_starts_at, datetime):
        raise TypeError(
            f"Expected datetime.datetime, got {type(week_starts_at)} instead: {week_starts_at}"
        )
    image_padding = pie_width / 5
    if "absents" in grid[week][day]:
        absents = grid[week][day]["absents"]
        if not isinstance(absents, list):
            raise TypeError(
                f"Expected list, got {type(absents)} instead: {absents} for week {week} day {day}"
            )
        image = image_loader.by_file_name(absent_grid_images[absents[0]["summary"]])
    else:
        image = image_loader.by_file_name(empty_image_file_name)
    if week_starts_at < tomorrow:
        plt.imshow(
            image,
            extent=(
                (pie_row_header_width + day * pie_width + image_padding) * width_aspect,
                (pie_row_header_width + (day + 1) * pie_width - image_padding) * width_aspect,
                week * pie_height + image_padding,
                (week + 1) * pie_height - image_padding,
            ),
            interpolation="bicubic",
        )


def highlight_today(grid: List[List[Dict[str, Any]]], today: datetime) -> None:
    """Draw a rectangle around the current day in the grid to highlight it.

    :param grid: The grid representing the schedule with structure [week][day]["date"].
    :param today: A datetime object indicating the current day.
    :return: None
    """
    grid_shift = (today - grid[0][0]["date"]).days
    day = grid_shift % WEEK_DAYS
    week = grid_shift // WEEK_DAYS
    plt.gca().add_patch(
        patches.Rectangle(
            ((pie_row_header_width + day * pie_width) * width_aspect, week * pie_height),
            pie_width * width_aspect * 0.98,
            pie_height,
            edgecolor="black",
            fill=False,
            linewidth=2,
        )
    )


def draw_pies(
    grid: List[List[Dict[str, Any]]],
    image_loader: ImageLoader,
    absent_grid_images: Dict[str, str],
    empty_image_file_name: str,
    weeks: int = 4,
) -> None:
    """Draw pie charts or images for each day in the provided grid based on the data provided.

    :param grid: The grid representing the schedule [week][day]["date"]/["values"].
    :param image_loader: Instance responsible for loading images.
    :param weeks: Number of weeks to consider. Default is 4.
    :param absent_grid_images: Dictionary mapping absent summary to image file names, which comes from the
                               "image_grid" key within the "absent" array in the settings.
    :param empty_image_file_name: File name of the image to use when there's no data.
    :return: None
    """
    daily_max = get_daily_max(grid)
    today = datetime.now(grid[0][0]["date"].tzinfo).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    tomorrow = today + timedelta(days=1)
    ax = plt.gcf().add_axes(
        [
            left_gap,
            0,
            1,
            pies_height,
        ],  # left, bottom, width, height, in fractions of figure width and height
        frameon=False,
        autoscale_on=False,
    )
    plt.axis("off")
    highlight_today(grid, today)
    draw_day_headers(grid)
    draw_week_headers(grid)
    for week in range(weeks):
        for day in range(len(grid[week])):
            values = grid[week][day]["values"]
            if sum(values) <= 0:
                draw_empty_pie(
                    grid,
                    image_loader,
                    week,
                    day,
                    absent_grid_images,
                    empty_image_file_name,
                    tomorrow,
                )
            else:
                draw_pie(week, day, values, daily_max)

    ax.set_ylim(0, pies_height)
    ax.set_xlim(0, width_aspect)
    ax.patch.set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])


def draw_weather(
    weather: Optional[WeatherData],
    rect: List[float],
    image_loader: ImageLoader,
) -> None:
    """Render the weather data onto a specified rectangle using matplotlib.

    :param weather: Weather data to render.
                    Only data for 1st day is used.
                    If weather is None, only the date is rendered.

    :param rect: A list of four float numbers [left, bottom, width, height] specifying the rectangle where the
                 weather data will be rendered.
    :type rect: List[float]

    :param image_loader: Instance responsible for loading images.
    :type image_loader: ImageLoader

    :return: None
    """
    ax = plt.axes(rect)
    plt.axis("off")
    ax.patch.set_visible(False)
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.set_ylim(-0.03, 1.03)
    ax.set_xlim(-0.03, 1.03)
    ax.text(
        0.5,
        1,
        datetime.now().strftime("%d %B"),
        horizontalalignment="center",
        verticalalignment="top",
    )
    if not weather:
        return
    ax.text(
        0.5,
        0,
        f"{round(weather.temp_min[0], 1)} °C … {round(weather.temp_max[0], 1)} °C",
        horizontalalignment="center",
        verticalalignment="bottom",
    )
    plt.imshow(
        image_loader.by_file_name(os.path.join(weather.images_folder, f"{weather.icon[0]}.png")),
        extent=[0.15, 0.85, 0.15, 0.85],
        interpolation="bilinear",  # 'bicubic'
    )


def place_text_and_image(
    ax: Axes,
    x_pos: Union[int, float],
    y_pos: Union[int, float],
    label: WeatherLabel,
    image_loader: ImageLoader,
) -> None:
    """Place text and image on the axes."""
    ax.text(x_pos, y_pos, label.summary, horizontalalignment="center", verticalalignment="top")

    if label.image:
        add_image_to_axes(ax, x_pos, y_pos, label, image_loader)


def add_image_to_axes(
    ax: Axes,
    x_pos: Union[int, float],
    y_pos: Union[int, float],
    label: WeatherLabel,
    image_loader: ImageLoader,
) -> None:
    """Add image to the axes."""
    legend_text_height = 0.13
    xlim, ylim = ax.get_xlim(), ax.get_ylim()
    xsz, ysz = xlim[1] - xlim[0], ylim[1] - ylim[0]
    x_scale = 1 / plot_height  # Clarify the logic behind this.
    x_val, y_val = (date2num(x_pos) - xlim[0]) / xsz * x_scale, (y_pos - ylim[0]) / ysz

    axes = plt.axes([plot_left, plot_bottom, plot_width, plot_height], label="2")
    configure_axes_for_image(axes)
    plt.imshow(
        image_loader.by_file_name(label.image),
        extent=(
            x_val - legend_image_sz / 2,
            x_val + legend_image_sz / 2,
            y_val - legend_image_sz - legend_text_height,
            y_val - legend_text_height,
        ),
        interpolation="bicubic",
    )


def configure_axes_for_image(axes: Axes) -> None:
    """Configure the axes for displaying an image."""
    plt.axis("off")
    axes.patch.set_visible(False)
    axes.set_xticklabels([])
    axes.set_yticklabels([])
    axes.set_ylim(0, 1)
    axes.set_xlim(0, 1 / plot_height)  # Used the earlier logic for x_scale directly here.


def draw_plot(
    x: List[datetime],
    y: List[List[float]],
    labels: List[WeatherLabel],
    rect: List[float],
    image_loader: ImageLoader,
    legend: str = "inside",
) -> None:
    """Render a stacked plot using matplotlib.

    :param x: List of datetime objects for the X-axis data.
    :type x: List[datetime]
    :param y: 2D list where each inner list represents a dataset for the plot, meant to be stacked.
    :type y: List[List[float]]
    :param labels: List of dictionaries containing labels for each dataset in `y`.
    :param rect: A list of four floats denoting the [left, bottom, width, height] of the rectangle where the plot is drawn.
    :type rect: List[float]
    :param image_loader: Instance responsible for image operations.
    :type image_loader: ImageLoader
    :param legend: Specifies the legend style. Can be 'inside', 'rectangle', or other values that result in no legend being drawn.
                   Defaults to 'inside'.
    :type legend: str

    :return: None
    """
    ax = plt.axes(rect)
    if len(x) > 0:
        days_on_plot = (x[-1] - x[0]).days
        if days_on_plot < 5 * 30:
            shortFmt = DateFormatter("%b %d")
        elif days_on_plot < 5 * 365:
            shortFmt = DateFormatter("%d")
        else:
            shortFmt = DateFormatter("%Y")
        ax.xaxis.set_major_formatter(shortFmt)
    legend_labels = [label.summary for label in labels]
    polies = ax.stackplot(x, y)
    ax.xaxis.set_major_locator(plt.MaxNLocator(6))
    ax.patch.set_visible(False)
    if legend == "rectangle":
        plt.legend(
            [plt.Rectangle((0, 0), 1, 1, fc=poly.get_facecolor()[0]) for poly in polies],
            legend_labels,
        )
    elif legend == "inside":
        # y_sum = np.sum(np.array(y), axis=0)
        # y_max = y_sum.max()
        for region, label in enumerate(labels):
            if not y[region]:
                return
            max_idx, _ = max(enumerate(y[region]), key=lambda item: item[1])
            x_pos, y_pos = x[max_idx], y[region][max_idx]
            place_text_and_image(ax, x_pos, y_pos, label, image_loader)


@cached(
    seconds=IMAGE_CACHED_SECONDS,
    trace_fmt="Use stored imaged without rendering (from {time})",
    daily_refresh=True,
)
def draw_calendar(
    grid: List[List[Dict[str, Union[datetime, List[int]]]]],
    x: List[datetime],
    y: List[List[float]],
    weather: Optional[WeatherData],
    dashboard: Dict[str, Union[str, List[Dict[str, str]]]],
    events: List[Dict[str, str]],
    absent_labels: List[Dict[str, str]],
    params: "ImageParams",
) -> bytes:
    """Draw IoT calendar as image, optimized for Amazon Kindle (600 x 800).

    To prepare data see functions in calendar_data.py

    :param grid:
        grid[weeks][days]
    :param x:
    :param y:
        y[event_list][x]
    :param weather: WeatherData
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
    plt.clf()
    plt.figure(figsize=(picture_width, picture_height), dpi=dpi, facecolor="white")
    absent_grid_images = {absent["summary"]: absent["image_grid"] for absent in absent_labels}
    image_loader = ImageLoader()
    plt.rcParams.update(plt.rcParamsDefault)
    with plt.style.context(params.style, after_reset=True):
        if int(params.xkcd):
            plt.xkcd()
        draw_weather(
            weather, rect=[0, plot_bottom, plot_left * 0.8, plot_height], image_loader=image_loader
        )
        draw_plot(
            x,
            y,
            [WeatherLabel(summary=event["summary"], image=event["image"]) for event in events],
            rect=[plot_left, plot_bottom, plot_width, plot_height],
            image_loader=image_loader,
        )
        empty_image_file_name = dashboard["empty_image"]
        if not isinstance(empty_image_file_name, str):
            raise TypeError(
                f"Expected filename in `empty_image`, got {type(empty_image_file_name)} instead: {empty_image_file_name}"
            )
        draw_pies(
            grid,
            image_loader=image_loader,
            weeks=weeks,
            absent_grid_images=absent_grid_images,
            empty_image_file_name=empty_image_file_name,
        )
        plt.gcf().canvas.draw()

        image = create_image(rotation_degrees=int(params.rotate), format=params.format)
        bytes_file = BytesIO()
        image.save(bytes_file, format=params.format)
        return bytes_file.getvalue()


def create_image(rotation_degrees: int, format: str) -> PIL.Image:  # pragma: no cover
    """Create image from matplotlib canvas."""
    if rotation_degrees % 90 != 0:
        raise ValueError("Degrees should be a multiple of 90")

    num_90_rotations = (rotation_degrees // 90) % 4
    buf = io.BytesIO()
    plt.savefig(buf, format=format)
    buf.seek(0)
    image = PIL.Image.open(buf)

    # Rotate the image
    img_np = np.array(image)
    img_np = np.rot90(img_np, k=num_90_rotations)

    return PIL.Image.fromarray(img_np)


def check(show: bool = True) -> None:  # pragma: no cover
    """Debugging function.

    To create the file with parameters for the check(), add the following code to the draw_calendar()

        call_params = dict(grid=grid, x=x, y=y, weather=weather, dashboard=dashboard, labels=labels,
            absent_labels=absent_labels, params=params)
        import json
        json.dump(call_params, open('draw_calendar_params.json', 'w'), default=str)
    """
    import json

    import dateutil

    call_params = json.load(
        open("tests/resources/draw_calendar_params_2.json", "r", encoding="utf-8")
    )
    for row in call_params["grid"]:
        for col in row:
            col["date"] = dateutil.parser.parse(col["date"])
    for i, day in enumerate(call_params["x"]):
        call_params["x"][i] = dateutil.parser.parse(call_params["x"][i])
    t0 = datetime.now()
    image_data = draw_calendar(
        call_params["grid"],
        call_params["x"],
        call_params["y"],
        WeatherData(**call_params["weather"]),
        call_params["dashboard"],
        call_params["labels"],
        call_params["absent_labels"],
        ImageParams(*call_params["params"]),
    )
    if show:
        t1 = datetime.now()
        print(f"Elapsed: {t1 - t0}")
        image_file = BytesIO(image_data)
        image = PIL.Image.open(image_file)
        image.show()


if __name__ == "__main__":  # pragma: no cover
    check()
