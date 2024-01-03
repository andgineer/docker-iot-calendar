import os
from datetime import datetime
from unittest.mock import MagicMock, Mock, call, patch

import pytest

import calendar_image
from calendar_image import (
    ImageLoader,
    draw_calendar,
    draw_day_headers,
    draw_empty_pie,
    draw_pie,
    draw_pies,
    draw_plot,
    draw_weather,
    draw_week_headers,
    highlight_today,
    pie_col_header_height,
    pie_height,
    pie_row_header_width,
    pie_scale,
    pie_width,
    WEEKS,
    width_aspect, ImageParams,
)
from models import WeatherData, WeatherLabel


@pytest.mark.parametrize(
    "input_grid",
    [
        [
            [
                {"date": datetime(2023, 8, 7)},  # Monday
                {"date": datetime(2023, 8, 8)},  # Tuesday
                {"date": datetime(2023, 8, 9)},  # Wednesday
                {"date": datetime(2023, 8, 10)},  # Thursday
                {"date": datetime(2023, 8, 11)},  # Friday
                {"date": datetime(2023, 8, 12)},  # Saturday
                {"date": datetime(2023, 8, 13)},  # Sunday
            ]
        ]
    ],
)
def test_draw_day_headers(input_grid):
    expected_calls = [
        call(
            (pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
            WEEKS * pie_height + 0.5 * pie_col_header_height,
            day_name,
            horizontalalignment="center",
            verticalalignment="center",
            fontsize=12,
        )
        for day, day_name in enumerate(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        )
    ]

    with patch("matplotlib.pyplot.text") as mock_text:
        draw_day_headers(input_grid)
        mock_text.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize(
    "input_grid,expected_calls",
    [
        (
            [
                [{"date": datetime(2023, 8, 7)}, {"date": datetime(2023, 8, 8)}],  # Week 1
                [{"date": datetime(2023, 8, 14)}, {"date": datetime(2023, 8, 15)}],  # Week 2
                [{"date": datetime(2023, 8, 21)}, {"date": datetime(2023, 8, 22)}],  # Week 3
                [{"date": datetime(2023, 8, 28)}, {"date": datetime(2023, 8, 29)}],  # Week 4
            ],
            [
                call(
                    pie_row_header_width * 0.5,
                    0.5 * pie_height,
                    "07\nAug",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=14,
                ),
                call(
                    pie_row_header_width * 0.5,
                    1.5 * pie_height,
                    "14\nAug",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=14,
                ),
                call(
                    pie_row_header_width * 0.5,
                    2.5 * pie_height,
                    "21\nAug",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=14,
                ),
                call(
                    pie_row_header_width * 0.5,
                    3.5 * pie_height,
                    "28\nAug",
                    horizontalalignment="center",
                    verticalalignment="center",
                    fontsize=14,
                ),
            ],
        )
    ],
)
def test_draw_week_headers(input_grid, expected_calls):
    with patch("matplotlib.pyplot.text") as mock_text:
        draw_week_headers(input_grid)
        mock_text.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize(
    "week, day, values, daily_max, expected_call",
    [
        (
            0,
            0,
            [10, 20, 30],
            100,
            call(
                [10, 20, 30],
                explode=[0.007, 0.007, 0.007],
                radius=0.6 * pie_height * pie_scale / 2,
                colors=["C0", "C1", "C2"],
                center=((pie_row_header_width + 0.5 * pie_width) * width_aspect, 0.5 * pie_height),
            ),
        )
    ],
)
def test_draw_pie(week, day, values, daily_max, expected_call):
    with patch("matplotlib.pyplot.pie") as mock_pie:
        draw_pie(week, day, values, daily_max)
        mock_pie.assert_called_once_with(*expected_call.args, **expected_call.kwargs)


@pytest.mark.parametrize(
    "grid, week, day, absent_grid_images, empty_image_file_name, tomorrow, expected_image_filename",
    [
        (
            [
                [
                    {"date": datetime(2023, 8, 10)},
                    {"date": datetime(2023, 8, 11), "absents": [{"summary": "AbsentA"}]},
                ],
            ],
            0,
            1,
            {"AbsentA": "absent_imageA.jpg"},
            "empty_image.jpg",
            datetime(2023, 8, 12),
            "absent_imageA.jpg",
        ),
        (
            [
                [
                    {"date": datetime(2023, 8, 10)},
                    {"date": datetime(2023, 8, 11)},
                    # ... other days
                ],
                # ... other weeks
            ],
            0,
            1,
            {"AbsentA": "absent_imageA.jpg"},
            "empty_image.jpg",
            datetime(2023, 8, 12),
            "empty_image.jpg",
        ),
    ],
)
def test_draw_empty_pie(
    grid, week, day, absent_grid_images, empty_image_file_name, tomorrow, expected_image_filename
):
    image_loader = MagicMock()
    image_mock = MagicMock()
    image_loader.by_file_name.return_value = image_mock

    with patch("matplotlib.pyplot.imshow") as mock_imshow:
        draw_empty_pie(
            grid, image_loader, week, day, absent_grid_images, empty_image_file_name, tomorrow
        )

        # Asserting the expected call to plt.imshow
        mock_imshow.assert_called_once_with(
            image_mock,
            extent=(
                (pie_row_header_width + day * pie_width + pie_width / 5) * width_aspect,
                (pie_row_header_width + (day + 1) * pie_width - pie_width / 5) * width_aspect,
                week * pie_height + pie_width / 5,
                (week + 1) * pie_height - pie_width / 5,
            ),
            interpolation="bicubic",
        )

        # Asserting the expected call to image_loader.by_file_name
        image_loader.by_file_name.assert_called_once_with(expected_image_filename)


def test_draw_today():
    # Sample grid
    grid = [
        [
            {"date": datetime(2023, 8, 9)},
            {"date": datetime(2023, 8, 10)},
        ],
        [
            {"date": datetime(2023, 8, 16)},
            {"date": datetime(2023, 8, 17)},
        ],
    ]

    # Mocking required objects
    with patch("matplotlib.pyplot.gca") as mock_gca:
        ax_mock = MagicMock()
        mock_gca.return_value = ax_mock

        # Call the function
        highlight_today(grid, datetime(2023, 8, 17))

        # Assert if add_patch was called on the Axes object
        ax_mock.add_patch.assert_called_once()

        # Extract the first argument passed (which should be a Rectangle) and check its properties
        rect = ax_mock.add_patch.call_args[0][0]

        # Here we only check a few properties, but more can be added as needed
        assert rect.get_xy() == (
            (pie_row_header_width + 1 * pie_width) * width_aspect,
            1 * pie_height,
        )
        assert rect.get_width() == pie_width * width_aspect * 0.98
        assert rect.get_height() == pie_height


def test_draw_pies():
    sample_grid = [
        [
            {"date": datetime(2023, 8, 7), "values": [10, 20]},
            {"date": datetime(2023, 8, 8), "values": [0], "absents": [{"summary": "AbsentA"}]},
            {"date": datetime(2023, 8, 9), "values": [15]},
            {"date": datetime(2023, 8, 10), "values": [0]},
            {"date": datetime(2023, 8, 11), "values": [10]},
            {"date": datetime(2023, 8, 12), "values": [25]},
            {"date": datetime(2023, 8, 13), "values": [0]},
        ],
        [
            {"date": datetime(2023, 8, 14), "values": [10, 20]},
            {"date": datetime(2023, 8, 15), "values": [0]},
            {"date": datetime(2023, 8, 9), "values": [15]},
            {"date": datetime(2023, 8, 10), "values": [0]},
            {"date": datetime(2023, 8, 11), "values": [10]},
            {"date": datetime(2023, 8, 12), "values": [25]},
            {"date": datetime(2023, 8, 13), "values": [0]},
        ],
    ]
    mock_image_loader = Mock()
    mock_image_loader.by_file_name = Mock(return_value="test_image")
    absent_images = {"AbsentA": "file1.jpg"}
    empty_image = "empty.jpg"

    # Mocking plt functions and your draw_pie and draw_empty_pie functions
    import matplotlib.pyplot as plt

    with patch.object(plt, "gcf", return_value=Mock()), patch(
        "calendar_image.draw_pie"
    ) as mock_draw_pie, patch("calendar_image.draw_empty_pie") as mock_draw_empty_pie, patch(
        "calendar_image.highlight_today"
    ) as mock_highlight_today, patch(
        "calendar_image.draw_day_headers"
    ) as mock_draw_day_headers, patch(
        "calendar_image.draw_week_headers"
    ) as mock_draw_week_headers:
        draw_pies(
            sample_grid,
            mock_image_loader,
            absent_grid_images=absent_images,
            empty_image_file_name=empty_image,
            weeks=2,
        )

    assert mock_draw_pie.call_count == 8

    # Assert draw_empty_pie was called for days with zero values
    assert mock_draw_empty_pie.call_count == 6

    mock_highlight_today.assert_called_once()
    mock_draw_day_headers.assert_called_once()
    mock_draw_week_headers.assert_called_once()

    expected_values = [[10, 20], [15], [10], [25], [10, 20], [15], [10], [25]]
    for idx, call in enumerate(mock_draw_pie.call_args_list):
        args, _ = call
        assert args[2] == expected_values[idx]


def test_draw_weather():
    # Sample data
    weather_data = WeatherData(
        temp_min=[15.5],
        temp_max=[25.8],
        images_folder="path_to_folder",
        icon=["sample_icon"],
        day=[],
    )
    rect = [0, 0, 1, 1]

    mock_image_loader = Mock(spec=ImageLoader)
    mock_image_loader.by_file_name.return_value = "test_image_path"

    # Mock plt functions
    import matplotlib.pyplot as plt

    with patch.object(plt, "axes", return_value=Mock()), patch.object(plt, "axis"), patch.object(
        plt, "imshow"
    ) as mock_imshow:
        draw_weather(weather_data, rect, mock_image_loader)

    # Asserts
    # Check if the image cache was called with the expected path
    expected_path = os.path.join(weather_data.images_folder, weather_data.icon[0] + ".png")
    mock_image_loader.by_file_name.assert_called_with(expected_path)

    # Assert the image was drawn at the expected extent
    mock_imshow.assert_called_once_with(
        "test_image_path", extent=(0.15, 0.85, 0.15, 0.85), interpolation="bilinear"
    )


def test_draw_plot():
    x = [datetime(2023, 1, 1), datetime(2023, 1, 2), datetime(2023, 1, 3)]
    y = [[1, 2, 3], [1, 2, 3]]
    labels = [
        WeatherLabel(summary="Label1", image="image1.png"),
        WeatherLabel(summary="Label2", image="image2.png"),
    ]
    rect = [0.1, 0.1, 0.8, 0.8]
    mock_image_loader = Mock()
    mock_image_loader.by_file_name.return_value = "some_image.png"

    mock_axes = Mock()
    mock_axes.get_xlim.return_value = (0, 10)  # Sample xlim values
    mock_axes.get_ylim.return_value = (0, 20)  # Sample ylim values

    import matplotlib.pyplot as plt

    with patch.object(plt, "axes", return_value=mock_axes), patch.object(
        plt, "axis", return_value=Mock()
    ), patch.object(plt, "imshow", return_value=Mock()), patch.object(
        plt, "legend", return_value=Mock()
    ), patch.object(
        plt, "text", return_value=Mock()
    ):
        draw_plot(x, y, labels, rect, mock_image_loader)

    # Assert that xlim and ylim were accessed twice each
    mock_axes.get_xlim.assert_called()
    assert mock_axes.get_xlim.call_count == 2

    mock_axes.get_ylim.assert_called()
    assert mock_axes.get_ylim.call_count == 2

    # Assert image cache was called with the provided image file names
    mock_image_loader.by_file_name.assert_has_calls([call("image1.png"), call("image2.png")])

    # Assert text was called for the labels
    mock_axes.text.assert_has_calls(
        [
            call(x[2], y[0][2], "Label1", horizontalalignment="center", verticalalignment="top"),
            call(x[2], y[1][2], "Label2", horizontalalignment="center", verticalalignment="top"),
        ]
    )

    # Assuming you have other mockable functions, you can add similar assertions


def test_draw_calendar():
    grid = [[{"date": datetime(2023, 8, 7), "values": [10, 20]}]]
    x = [datetime(2023, 8, 7)]
    y = [[10]]
    weather = WeatherData(
        temp_min=[15.0],
        temp_max=[20.0],
        icon=["cloudy"],
        day=[datetime(2023, 8, 7)],
        images_folder="",
    )
    dashboard = {
        "summary": "Summary",
        "empty_image": "path/to/image.jpg",
        "absent": [{"summary": "Holiday", "image_grid": "path/to/holiday.jpg"}],
    }
    events = [{"summary": "Summary", "image": "path/to/image.jpg"}]
    absent_labels = [
        {
            "summary": "Holiday",
            "image_grid": "path/to/holiday.jpg",
            "image_plot": "path/to/holiday_plot.jpg",
        }
    ]
    params = (
        Mock()
    )  # This will need to be an instance of ImageParams or a Mock object representing it
    params.xkcd = "0"
    params.rotate = "0"

    # Mocking plt and other external calls
    with patch("matplotlib.pyplot.clf"), patch("matplotlib.pyplot.figure"), patch(
        "matplotlib.pyplot.rcParams.update"
    ), patch("matplotlib.pyplot.style.context"), patch(
        "calendar_image.draw_weather"
    ) as mock_draw_weather, patch(
        "calendar_image.draw_plot"
    ) as mock_draw_plot, patch(
        "calendar_image.draw_pies"
    ) as mock_draw_pies, patch(
        "calendar_image.ImageLoader"
    ) as mock_image_loader, patch(
        "numpy.rot90"
    ) as mock_np_rot90, patch(
        "PIL.Image.fromarray"
    ) as mock_fromarray, patch(
        "PIL.Image.open"
    ) as mock_image_open:
        mock_image_loader.return_value = Mock()
        mock_np_rot90.return_value = Mock()
        mock_fromarray.return_value = Mock(save=Mock())

        result = draw_calendar(grid, x, y, weather, dashboard, events, absent_labels, params)

        mock_draw_weather.assert_called_once_with(
            weather,
            rect=(0, 0.6833333333333333, 0.24, 0.29166666666666663),
            image_loader=mock_image_loader.return_value,
        )
        mock_draw_plot.assert_called_once_with(
            x,
            y,
            [WeatherLabel(summary=event["summary"], image=event["image"]) for event in events],
            rect=(0.3, 0.6833333333333333, 0.6749999999999999, 0.29166666666666663),
            image_loader=mock_image_loader.return_value,
        )
        mock_draw_pies.assert_called_once_with(
            grid,
            image_loader=mock_image_loader.return_value,
            weeks=4,
            absent_grid_images={"Holiday": "path/to/holiday.jpg"},
            empty_image_file_name="path/to/image.jpg",
        )

        assert isinstance(result, bytes)
        mock_image_loader.assert_called_once()
        mock_np_rot90.assert_called_once()
        mock_fromarray.assert_called_once()
        mock_image_open.assert_called_once()


@pytest.mark.benchmark
def test_draw_benchmark(benchmark):
    benchmark(calendar_image.check, show=False)