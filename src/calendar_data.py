"""
Prepare data for calendar_image.py
"""

def interval_by_time(time, by_time=[]):
    if len(by_time) == 0:
        return 0
    for interval_idx, interval in enumerate(by_time):
        if 'before' in interval:
            interval_end_parts = [int(s) for s in interval['before'].split(':')]
            interval_end = time.replace(hour=interval_end_parts[0], minute=interval_end_parts[1], second=interval_end_parts[2])
            if time < interval_end:
                return interval_idx
    else:
        return interval_idx


def get_values_empty_array(by_time):
    if len(by_time) == 0:
        values_array_len = 1
    else:
        values_array_len = len(by_time)
    return np.zeros(values_array_len)


def event_duration(event):
    return int((event['end'] - event['start']).seconds / 60)


def events_to_weeks_grid(events, summary, weeks=4, by_time=[]):
    """
    [
        [{'date': week0_day0_date, 'values': values_list}, ...],
        [{'date': week1_day0_date, 'values': values_list}, ...],
    ]
    """
    if len(events) > 0:
        tzinfo = events[0]['start'].tzinfo
    else:
        tzinfo = None
    last_date_in_grid = datetime.datetime.now(tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
    today_week_day = last_date_in_grid.weekday()
    first_date_in_grid = last_date_in_grid - datetime.timedelta(days=weeks * 7 - (7 - (today_week_day + 1)) - 1)
    grid = []

    for week in range(weeks):
        week_array = []
        for day in range(7):
            week_array.append({
                'date': first_date_in_grid + datetime.timedelta(weeks=week, days=day),
                'values': get_values_empty_array(by_time)
            })
        grid.append(week_array)
    if len(events) == 0:
        return grid
    for event in events:
        time = event['start']
        if time >= first_date_in_grid and time < last_date_in_grid + datetime.timedelta(days=1):
            week = int((time - first_date_in_grid).days // 7)
            day = int((time - first_date_in_grid -datetime.timedelta(weeks=week)).days)
            value_idx = interval_by_time(time, by_time)
            grid[week][day]['values'][value_idx] += event_duration(event)
    return grid


def events_to_array(events, summary, by_time=[]):
    a = []
    for event in events:
        date = event['start'].replace(hour=0, minute=0, second=0, microsecond=0)
        value_idx = interval_by_time(event['start'], by_time)
        if len(a) == 0 or a[-1]['date'] != date:
            a.append({'date': date, 'values': get_values_empty_array(by_time)})
        a[-1]['values'][value_idx] += event_duration(event)
    return [event['date'] for event in a], [[event['values'][0] for event in a], [event['values'][1] for event in a]]


if __name__ == '__main__':
    x, y = events_to_array(
        events,
        'white',
        by_time=[{'before': '11:00:00', 'summary': 'morning {button}'}, {'summary': 'evening {button}'}]
    )
    print(x, y)
    grid = events_to_weeks_grid(
        events,
        'white',
        by_time=[{'before': '11:00:00', 'summary': 'morning {button}'}, {'summary': 'evening {button}'}]
    )

