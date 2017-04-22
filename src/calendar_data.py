"""
Prepare data for calendar_image.py
"""
import copy
import datetime
from dateutil.tz import tzoffset
import collections


# def dashboard_list(settings):
#     result = [dashboard['summary'] for dashboard in settings['dashboards']]
#     return result

def preprocess_actions(button, button_settings):
    """
    Add summary (with button name value) if there is no one.
    Substitutes {button} with button name in parameters.
    """
    def subst(param):
        if isinstance(param, str):
            return param.format(button=button)
        if isinstance(param, collections.Mapping):
            result = {}
            for item in param:
                result[item] = subst(param[item])
            return result
        if isinstance(param, collections.Iterable):
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
    """
    :param settings:
    :param dashboard_name:
    :return: list of calendar actions for the dashboard_name
    [{'summary': summary, 'calendar_id': calendar_id}, ...]
    """
    result = []
    for button in settings['actions']:
        if button != '__DEFAULT__':
            button_actions = settings['actions'][button]
            actions = preprocess_actions(button, button_actions)
            print(actions)
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
    return grid


def events_to_array(events):
    DATE_FMT = '%Y%m%d'
    by_date = {}
    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            date = event['start'].replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = date.strftime(DATE_FMT)
            if date_str not in by_date:
                by_date[date_str] = [0 for _ in range(len(events))]
            by_date[date_str][event_list_idx] += event_duration(event)
    x = [datetime.datetime.strptime(date_str, DATE_FMT) for date_str in sorted(by_date.keys())]
    y = []
    for event_list_idx in range(len(events)):
        y.append([by_date[date_str][event_list_idx] for date_str in sorted(by_date.keys())])
    return x, y


def test():
    from iot_calendar import load_settings
    settings = load_settings()
    print(calendar_events_list(settings, 'anna_work_out'))
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

