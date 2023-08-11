"""
Prepare data for calendar_image.py
"""

import copy
import datetime
from dateutil.tz import tzoffset
import collections.abc
import pprint


def preprocess_actions(button, button_settings):
    """Add summary (with button name value) if there is no one.

    Substitutes {button} with button name in parameters.
    """
    def subst(param):
        """Substitute {button} with button name in parameters."""
        if isinstance(param, str):
            return param.format(button=button)
        if isinstance(param, collections.abc.Mapping):
            result = {}
            for item in param:
                result[item] = subst(param[item])
            return result
        if isinstance(param, collections.abc.Iterable):
            result = []
            for item in param:
                result.append(subst(item))
            return result
        return param

    actions = copy.deepcopy(button_settings['actions'])
    for action in actions:
        if 'summary' not in action:
            if 'summary' in button_settings:
                action['summary'] = button_settings['summary']
            else:
                action['summary'] = button
        for param in action:
            action[param] = subst(action[param])
    return actions


def calendar_events_list(settings, dashboard_name):
    """List of calendar events for the dashboard_name.

    :param settings:
    :param dashboard_name:
    :return: list of calendar actions for the dashboard_name
    [{'summary': summary, 'calendar_id': calendar_id, 'image': image_file_name}, ...]
    """
    result = []
    for button in settings['actions']:
        if button != '__DEFAULT__':
            button_actions = settings['actions'][button]
            actions = preprocess_actions(button, button_actions)
            print('Processed actions')
            pprint.pprint(actions)
            for action in actions:
                if 'type' in action and action['type'] == 'calendar'\
                        and 'dashboard' in action and action['dashboard'] == dashboard_name:
                    if isinstance(action['summary'], list):
                        for interval in action['summary']:
                            a = copy.deepcopy(action)
                            a['summary'] = interval['summary']
                            if 'image' in interval:
                                a['image'] = interval['image']
                            result.append(a)
                    else:
                        result.append(copy.deepcopy(action))
    return result


def dashboard_absent_events_list(settings, dashboard_name):
    """List of calendar absent events for the dashboard_name."""
    dashboards = settings['dashboards']
    if dashboard_name in dashboards and 'absent' in dashboards[dashboard_name]:
        return dashboards[dashboard_name]['absent']
    else:
        return []


def event_duration(event):
    """Duration of event in minutes."""
    delta = event['end'] - event['start']
    return (delta.days * 24 * 60) + (delta.seconds // 60)


def events_to_weeks_grid(events, absents, weeks=4):
    """Convert list of events to weeks grid.

    events: list of events lists
    returns list of weeks:
    [
        [{'date': week0_Monday_date, 'values': values_list}, {'date': week0_Tuesday_date, 'values': values_list}, ...],
        [{'date': week1_Monday_date, 'values': values_list}, {'date': week1_Tuesday_date, 'values': values_list}, ...],
        ...
        [{'date': week<weeks-1>_Monday_date, 'values': values_list}, {'date': week<weeks-1>_Tuesday_date, 'values': values_list}, ...]
    ]
    Each day may contain 'absent' param with image filepath that should be shown if in values for this day all zeroes.
    """
    def get_tzinfo(events):
        """Get tzinfo from any event."""
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
                'values': [0 for _ in range(len(events))]
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
    for absent_list_idx, absent_list in enumerate(absents):
        for absent in absent_list:
            start = absent['start'].replace(hour=0, minute=0, second=0, microsecond=0)
            end = absent['end'].replace(hour=0, minute=0, second=0, microsecond=0)
            if first_date_in_grid <= start < tomorrow or first_date_in_grid <= end < tomorrow:
                for absent_day in range((end - start).days + 1):
                    absent_date = start + datetime.timedelta(days=absent_day)
                    if first_date_in_grid <= absent_date < tomorrow:
                        week = int((absent_date - first_date_in_grid).days // 7)
                        day = int((absent_date - first_date_in_grid -datetime.timedelta(weeks=week)).days)
                        if 'absents' not in grid[week][day]:
                            grid[week][day]['absents'] = []
                        grid[week][day]['absents'].append({'summary': absent['summary']})
    return grid


def events_to_array(events, absents):
    """Convert list of events to array."""
    DATE_FMT = '%Y%m%d'
    by_date = {}
    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            date = event['start'].replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = date.strftime(DATE_FMT)
            if date_str not in by_date:
                by_date[date_str] = [0 for _ in range(len(events))]
            by_date[date_str][event_list_idx] += event_duration(event)
    # for all absences add days with zeroes to see the gap on plot
    for absent_list in absents:
        for absent in absent_list:
            start = absent['start'].replace(hour=0, minute=0, second=0, microsecond=0)
            end = absent['end'].replace(hour=0, minute=0, second=0, microsecond=0)
            for day in range((end - start).days):
                date = start + datetime.timedelta(days=day)
                date_str = date.strftime(DATE_FMT)
                if date_str not in by_date:
                    by_date[date_str] = [0 for _ in range(len(events))]
    x = [datetime.datetime.strptime(date_str, DATE_FMT) for date_str in sorted(by_date.keys())]
    y = [
        [
            by_date[date_str][event_list_idx]
            for date_str in sorted(by_date.keys())
        ]
        for event_list_idx in range(len(events))
    ]
    return x, y


def check():  # pragma: no cover
    """Debug function."""
    from iot_calendar import load_settings
    settings = load_settings()
    print(calendar_events_list(settings, 'anna_work_out'))
    events = [
        [{'end': datetime.datetime(2017, 4, 14, 8, 22, 30, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 14, 8, 15, 39, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 17, 8, 27, 43, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 17, 8, 16, 35, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 18, 8, 18, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 18, 8, 12, 9, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 19, 8, 24, 26, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 19, 8, 17, 8, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 20, 8, 22, 24, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 20, 8, 16, 34, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 21, 8, 25, 27, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 21, 8, 20, 26, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 22, 10, 16, 5, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 22, 10, 10, 7, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 23, 10, 43, 37, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 23, 10, 38, 45, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 24, 8, 22, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 24, 8, 14, 47, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'},
               {'end': datetime.datetime(2017, 4, 25, 8, 15, 7, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 25, 8, 10, 58, tzinfo=tzoffset(None, 10800)),
                'summary': 'Morning work-out'}
         ],
        [{'end': datetime.datetime(2017, 4, 13, 20, 23, tzinfo=tzoffset(None, 10800)),
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
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 4, 19, 17, 21, 57, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 19, 16, 49, 55, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 4, 21, 17, 5, 4, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 21, 16, 26, 51, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 4, 23, 19, 18, 49, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 23, 18, 58, 12, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 4, 25, 20, 17, 14, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 4, 25, 20, 3, 25, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 5, 10, 17, 59, 18, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 5, 10, 17, 36, 51, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'},
               {'end': datetime.datetime(2017, 5, 12, 20, 49, 9, tzinfo=tzoffset(None, 10800)),
                'start': datetime.datetime(2017, 5, 12, 20, 9, 32, tzinfo=tzoffset(None, 10800)),
                'summary': 'Physiotherapy'}
         ]
    ]
    absents = [[{'end': datetime.datetime(2017, 5, 7, 23, 59, 59, tzinfo=tzoffset(None, 10800)),
                 'start': datetime.datetime(2017, 4, 26, 0, 0, tzinfo=tzoffset(None, 10800)),
                 'summary': 'Sick'}],
               []]
    x, y = events_to_array(events, absents)
    pprint.pprint(x)
    pprint.pprint(y)
    grid = events_to_weeks_grid(events, absents)
    pprint.pprint(grid)


if __name__ == '__main__':
    check()

