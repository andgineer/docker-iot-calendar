import pytest
from unittest.mock import patch, call, MagicMock
from datetime import datetime
from calendar_image import pie_row_header_width, pie_width, pie_height, pie_col_header_height, weeks, draw_day_headers, \
    width_aspect, draw_week_headers, pie_scale, draw_pie, draw_empty_pie, highlight_today


@pytest.mark.parametrize('input_grid', [
    [
        [
            {'date': datetime(2023, 8, 7)},  # Monday
            {'date': datetime(2023, 8, 8)},  # Tuesday
            {'date': datetime(2023, 8, 9)},  # Wednesday
            {'date': datetime(2023, 8, 10)},  # Thursday
            {'date': datetime(2023, 8, 11)},  # Friday
            {'date': datetime(2023, 8, 12)},  # Saturday
            {'date': datetime(2023, 8, 13)}  # Sunday
        ]
    ]
])
def test_draw_day_headers(input_grid):
    expected_calls = [
        call((pie_row_header_width + (day + 0.5) * pie_width) * width_aspect,
             weeks * pie_height + 0.5 * pie_col_header_height,
             day_name,
             horizontalalignment='center', verticalalignment='center', fontsize=12)
        for day, day_name in enumerate(['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'])
    ]

    with patch('matplotlib.pyplot.text') as mock_text:
        draw_day_headers(input_grid)
        mock_text.assert_has_calls(expected_calls, any_order=False)


@pytest.mark.parametrize('input_grid,expected_calls', [
    (
        [
            [{'date': datetime(2023, 8, 7)}, {'date': datetime(2023, 8, 8)}], # Week 1
            [{'date': datetime(2023, 8, 14)}, {'date': datetime(2023, 8, 15)}], # Week 2
            [{'date': datetime(2023, 8, 21)}, {'date': datetime(2023, 8, 22)}], # Week 3
            [{'date': datetime(2023, 8, 28)}, {'date': datetime(2023, 8, 29)}]  # Week 4
        ],
        [
            call(pie_row_header_width * 0.5, 0.5 * pie_height, '07\nAug', horizontalalignment='center', verticalalignment='center', fontsize=14),
            call(pie_row_header_width * 0.5, 1.5 * pie_height, '14\nAug', horizontalalignment='center', verticalalignment='center', fontsize=14),
            call(pie_row_header_width * 0.5, 2.5 * pie_height, '21\nAug', horizontalalignment='center', verticalalignment='center', fontsize=14),
            call(pie_row_header_width * 0.5, 3.5 * pie_height, '28\nAug', horizontalalignment='center', verticalalignment='center', fontsize=14)
        ]
    )
])
def test_draw_week_headers(input_grid, expected_calls):
    with patch('matplotlib.pyplot.text') as mock_text:
        draw_week_headers(input_grid)
        mock_text.assert_has_calls(expected_calls, any_order=False)

@pytest.mark.parametrize('week, day, values, daily_max, expected_call', [
    (
        0, 0, [10, 20, 30], 100,
        call(
            [10, 20, 30],
            explode=[0.007, 0.007, 0.007],
            radius=0.6 * pie_height * pie_scale / 2,
            colors=['C0', 'C1', 'C2'],
            center=(
                (pie_row_header_width + 0.5 * pie_width) * width_aspect,
                0.5 * pie_height
            )
        )
    )
])
def test_draw_pie(week, day, values, daily_max, expected_call):
    with patch('matplotlib.pyplot.pie') as mock_pie:
        draw_pie(week, day, values, daily_max)
        mock_pie.assert_called_once_with(*expected_call.args, **expected_call.kwargs)


@pytest.mark.parametrize('grid, week, day, absent_grid_images, empty_image_file_name, tomorrow, expected_image_filename', [
    (
        [
            [
                {'date': datetime(2023, 8, 10)},
                {'date': datetime(2023, 8, 11), 'absents': [{'summary': 'AbsentA'}]},
                # ... other days
            ],
            # ... other weeks
        ],
        0, 1,
        {'AbsentA': 'absent_imageA.jpg'},
        'empty_image.jpg',
        datetime(2023, 8, 12),
        'absent_imageA.jpg'
    ),
    (
        [
            [
                {'date': datetime(2023, 8, 10)},
                {'date': datetime(2023, 8, 11)},
                # ... other days
            ],
            # ... other weeks
        ],
        0, 1,
        {'AbsentA': 'absent_imageA.jpg'},
        'empty_image.jpg',
        datetime(2023, 8, 12),
        'empty_image.jpg'
    ),
])
def test_draw_empty_pie(grid, week, day, absent_grid_images, empty_image_file_name, tomorrow, expected_image_filename):
    image_cache = MagicMock()
    image_mock = MagicMock()
    image_cache.by_file_name.return_value = image_mock

    with patch('matplotlib.pyplot.imshow') as mock_imshow:
        draw_empty_pie(grid, image_cache, week, day, absent_grid_images, empty_image_file_name, tomorrow)

        # Asserting the expected call to plt.imshow
        mock_imshow.assert_called_once_with(
            image_mock,
            extent=(
                (pie_row_header_width + day * pie_width + pie_width / 5) * width_aspect,
                (pie_row_header_width + (day + 1) * pie_width - pie_width / 5) * width_aspect,
                week * pie_height + pie_width / 5,
                (week + 1) * pie_height - pie_width / 5
            ),
            interpolation='bicubic'
        )

        # Asserting the expected call to image_cache.by_file_name
        image_cache.by_file_name.assert_called_once_with(expected_image_filename)


def test_draw_today():
    # Sample grid
    grid = [
        [
            {'date': datetime(2023, 8, 9)},
            {'date': datetime(2023, 8, 10)},
            # ... other days
        ],
        [
            {'date': datetime(2023, 8, 16)},
            {'date': datetime(2023, 8, 17)},
            # ... other days
        ]
        # ... other weeks
    ]

    # Mocking required objects
    with patch('matplotlib.pyplot.gca') as mock_gca:
        ax_mock = MagicMock()
        mock_gca.return_value = ax_mock

        # Call the function
        highlight_today(grid, datetime(2023, 8, 17))

        # Assert if add_patch was called on the Axes object
        ax_mock.add_patch.assert_called_once()

        # Extract the first argument passed (which should be a Rectangle) and check its properties
        rect = ax_mock.add_patch.call_args[0][0]

        # Here we only check a few properties, but more can be added as needed
        assert rect.get_xy() == ((pie_row_header_width + 1 * pie_width) * width_aspect, 1 * pie_height)
        assert rect.get_width() == pie_width * width_aspect * 0.98
        assert rect.get_height() == pie_height
