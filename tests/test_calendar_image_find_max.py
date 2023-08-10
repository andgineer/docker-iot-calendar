from calendar_image import get_daily_max


def test_find_max_total_empty_grid():
    assert get_daily_max([]) == 0

def test_find_max_total_single_entry():
    grid = [[{'values': [10]}]]
    assert get_daily_max(grid) == 10

def test_find_max_total_multiple_entries_single_day():
    grid = [[{'values': [5, 15]}, {'values': [3, 2]}]]
    assert get_daily_max(grid) == 20

def test_find_max_total_multiple_entries_multiple_days():
    grid = [
        [{'values': [2, 2]}, {'values': [3, 3]}],
        [{'values': [4, 4]}, {'values': [1, 2, 3]}],
    ]
    assert get_daily_max(grid) == 8

def test_find_max_total_with_negative_values():
    grid = [
        [{'values': [-2, 2]}, {'values': [3, -3]}],
        [{'values': [4, -4]}, {'values': [1, -1, 3]}],
    ]
    assert get_daily_max(grid) == 3

def test_find_max_total_all_zeros():
    grid = [
        [{'values': [0, 0]}, {'values': [0, 0]}],
        [{'values': [0, 0]}, {'values': [0, 0]}],
    ]
    assert get_daily_max(grid) == 0

