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


def event_duration(event):
    return int((event['end'] - event['start']).seconds / 60)


def events_to_weeks_grid(events, weeks=4):
    """
    events: list of events lists
    returns weeks list:
    [
        [{'date': week0_Monday_date, 'values': values_list}, {'date': week0_Tuesday_date, 'values': values_list}, ...],
        [{'date': week1_Monday_date, 'values': values_list}, {'date': week1_Tuesday_date, 'values': values_list}, ...],
        ...
        [{'date': week<weeks-1>_Monday_date, 'values': values_list}, {'date': week<weeks-1>_Tuesday_date, 'values': values_list}, ...]
    ]
    """
    def get_tzinfo(events):
        """get tzinfo from any event"""
        for event_list in events:
            for event in event_list:
                return event['start'].tzinfo
        return None
    tzinfo = get_tzinfo(events)
    today = datetime.datetime.now(tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + datetime.timedelta(days=1)
    today_week_day = today.weekday()
    first_date_in_grid = today - datetime.timedelta(days=weeks * 7 - (7 - (today_week_day + 1)) - 1)
    grid = []
    for week in range(weeks):
        week_array = []
        for day in range(7):
            week_array.append({
                'date': first_date_in_grid + datetime.timedelta(weeks=week, days=day),
                'values': np.zeros(len(events))
            })
        grid.append(week_array)
    if len(events) == 0:
        return grid
    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            time = event['start']
            if first_date_in_grid <= time < tomorrow:
                week = int((time - first_date_in_grid).days // 7)
                day = int((time - first_date_in_grid -datetime.timedelta(weeks=week)).days)
                grid[week][day]['values'][event_list_idx] += event_duration(event)
    return grid


def events_to_array(events):
    DATE_FMT = '%Y%m%d'
    by_date = {}
    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            date = event['start'].replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = date.strftime(DATE_FMT)
            if date_str not in by_date:
                by_date[date_str] = np.zeros(len(events))
            by_date[date_str][event_list_idx] += event_duration(event)
    x = [datetime.datetime.strptime(date_str, DATE_FMT) for date_str in sorted(by_date.keys())]
    y = []
    for event_list_idx in range(len(events)):
        y.append([by_date[date_str][event_list_idx] for date_str in sorted(by_date.keys())])
    return x, y


def test():
    events = [
        [
            {'end': datetime.datetime(2017, 4, 7, 8, 17, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 7, 8, 2, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
            {'end': datetime.datetime(2017, 4, 8, 11, 11, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 8, 11, 2, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
            {'end': datetime.datetime(2017, 4, 12, 8, 30, 11, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 12, 8, 20, 50, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
            {'end': datetime.datetime(2017, 4, 13, 8, 19, 22, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 13, 8, 13, 24, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
            {'end': datetime.datetime(2017, 4, 14, 8, 22, 30, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 14, 8, 15, 39, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
            {'end': datetime.datetime(2017, 4, 17, 8, 27, 43, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 17, 8, 16, 35, tzinfo=tzoffset(None, 10800)),
             'summary': 'Morning work-out'},
        ],
        [
            {'end': datetime.datetime(2017, 4, 6, 20, 17, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 6, 20, 2, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 7, 19, 12, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 7, 18, 55, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 11, 19, 53, 19, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 11, 19, 33, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 12, 20, 39, 3, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 12, 20, 18, 29, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 13, 20, 23, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 13, 20, 3, 5, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 14, 17, 26, 47, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 14, 16, 55, 56, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 16, 18, 20, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 16, 17, 48, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'},
            {'end': datetime.datetime(2017, 4, 17, 17, 51, 35, tzinfo=tzoffset(None, 10800)),
             'start': datetime.datetime(2017, 4, 17, 17, 28, 31, tzinfo=tzoffset(None, 10800)),
             'summary': 'Physiotherapy'}
        ]
    ]
    x, y = events_to_array(events)
    print(x, y)
    grid = events_to_weeks_grid(events)
    print(grid)


if __name__ == '__main__':
    test()

