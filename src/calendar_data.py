"""
Prepare data for calendar_image.py
"""
import copy
import datetime
import numpy as np


class CalendarData(object):
    def __init__(self, settings):
        self.settings = settings
        self.actions = settings['actions']

    def preprocess_actions(self, button, actions):
        """
        Add summary (with button name value) if there is no one.
        Substitutes {button} with button name in parameters
        and {summary} with summary parameter.
        """
        actions = copy.deepcopy(actions)
        for action in actions:
            if 'summary' not in action:
                action['summary'] = button
            summary = action['summary'].format(button=button)
            for param in action:
                if isinstance(action[param], str):
                    action[param] = action[param].format(button=button, summary=summary)
        return actions

    def dashboard_actions(self, dashboard):
        """Returns list of actions for the dashboard"""
        result = []
        for button in self.actions:
            if button != '__DEFAULT__':
                actions = self.actions[button]['actions']
                actions = self.preprocess_actions(button, actions)
                for act in actions:
                    result.append(act)
        return result


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


def test():
    events = [
        {'end': datetime.datetime(2017, 4, 6, 20, 17, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 6, 20, 2, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 7, 8, 17, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 7, 8, 2, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 7, 19, 12, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 7, 18, 55, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 8, 11, 11, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 8, 11, 2, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 11, 19, 53, 19, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 11, 19, 33, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 12, 8, 30, 11, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 12, 8, 20, 50, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 12, 20, 39, 3, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 12, 20, 18, 29, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 13, 8, 19, 22, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 13, 8, 13, 24, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 13, 20, 23, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 13, 20, 3, 5, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 14, 8, 22, 30, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 14, 8, 15, 39, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 14, 17, 26, 47, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 14, 16, 55, 56, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 16, 18, 20, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 16, 17, 48, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 17, 8, 27, 43, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 17, 8, 16, 35, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'},
        {'end': datetime.datetime(2017, 4, 17, 17, 51, 35, tzinfo=tzoffset(None, 10800)),
         'start': datetime.datetime(2017, 4, 17, 17, 28, 31, tzinfo=tzoffset(None, 10800)),
         'summary': '#white'}
    ]
    x, y = events_to_array(
        events,
        'white',
        by_time=[{'before': '11:00:00', 'summary': 'morning {summary}'}, {'summary': 'evening {summary}'}]
    )
    print(x, y)
    grid = events_to_weeks_grid(
        events,
        'white',
        by_time=[{'before': '11:00:00', 'summary': 'morning {summary}'}, {'summary': 'evening {summary}'}]
    )
    print(grid)


if __name__ == '__main__':
    test()

