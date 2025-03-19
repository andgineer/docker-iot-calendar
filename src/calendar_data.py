"""Prepare data for calendar_image.py."""

import collections.abc
import copy
import datetime
import pprint
from typing import Any, Optional, Union, cast


def preprocess_actions(  # noqa: C901
    button: str,
    button_settings: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    """Add summary (with button name value) if there is no one.

    Substitutes {button} with button name in parameters.
    """

    def subst(param: Any) -> Any:
        """Substitute {button} with button name in parameters."""
        if isinstance(param, str):
            return param.format(button=button)
        if isinstance(param, collections.abc.Mapping):
            result_map = {}
            for item in param:
                result_map[item] = subst(param[item])
            return result_map
        if isinstance(param, collections.abc.Iterable):
            result = []
            for item in param:
                result.append(subst(item))
            return result
        return param

    actions = copy.deepcopy(button_settings["actions"])
    for action in actions:
        if "summary" not in action:
            action["summary"] = button_settings.get("summary", button)
        for param in action:
            action[param] = subst(action[param])
    return actions


def calendar_events_list(
    settings: dict[str, Any],
    dashboard_name: str,
) -> list[dict[str, Union[str, Any]]]:
    """List of calendar events for the dashboard_name.

    :param settings: Dictionary containing actions.
    :param dashboard_name: Name of the dashboard to filter by.
    :return: list of calendar actions for the dashboard_name
    [{'summary': summary, 'calendar_id': calendar_id, 'image': image_file_name}, ...]
    """

    def is_relevant_action(action: dict[str, Any]) -> bool:
        return action.get("type") == "calendar" and action.get("dashboard") == dashboard_name

    def process_action(action: dict[str, Any]) -> list[dict[str, Any]]:
        """Process an action and return list of actions based on summary."""
        if isinstance(action["summary"], list):
            return [
                {
                    **copy.deepcopy(action),
                    "summary": interval["summary"],
                    "image": interval.get("image", None),
                }
                for interval in action["summary"]
            ]
        return [copy.deepcopy(action)]

    all_actions = [
        action
        for button, button_actions in settings["events"].items()
        if button != "__DEFAULT__"
        for action in preprocess_actions(button, button_actions)
        if is_relevant_action(action)
    ]

    return [processed for action in all_actions for processed in process_action(action)]


def dashboard_absent_events_list(
    settings: dict[str, Any],
    dashboard_name: str,
) -> list[dict[str, Any]]:
    """List of calendar absent events for the dashboard_name."""
    dashboards = settings["dashboards"]
    if dashboard_name in dashboards and "absent" in dashboards[dashboard_name]:
        return cast(list[dict[str, Any]], dashboards[dashboard_name]["absent"])
    return []


def event_duration(event: dict[str, Any]) -> int:
    """Duration of event in minutes."""
    delta = cast(datetime.datetime, event["end"]) - cast(datetime.datetime, event["start"])
    return (delta.days * 24 * 60) + (delta.seconds // 60)


def events_to_weeks_grid(  # noqa: C901
    events: list[list[dict[str, Any]]],
    absents: list[list[dict[str, Any]]],
    weeks: int = 4,
) -> list[list[dict[str, Union[datetime.datetime, list[int], list[dict[str, str]]]]]]:
    """Convert list of events to weeks grid."""

    def get_tzinfo(events: list[list[dict[str, Any]]]) -> Optional[datetime.tzinfo]:
        """Get tzinfo from any event."""
        for event_list in events:
            for event in event_list:
                return event["start"].tzinfo  # type: ignore
        return None

    def initialize_grid(
        first_date: datetime.datetime,
    ) -> list[list[dict[str, Union[datetime.datetime, list[int], list[dict[str, str]]]]]]:
        """Initialize grid with empty values."""
        return [
            [
                {
                    "date": first_date + datetime.timedelta(weeks=week, days=day),
                    "values": [0 for _ in range(len(events))],
                }
                for day in range(7)
            ]
            for week in range(weeks)
        ]

    tzinfo = get_tzinfo(events)
    today = datetime.datetime.now(tzinfo).replace(hour=0, minute=0, second=0, microsecond=0)
    tomorrow = today + datetime.timedelta(days=1)
    today_week_day = today.weekday()
    first_date_in_grid = today - datetime.timedelta(
        days=weeks * 7 - (7 - (today_week_day + 1)) - 1,
    )
    dict_type = dict[str, Union[datetime.datetime, list[int], list[dict[str, str]]]]
    grid: list[list[dict_type]] = initialize_grid(first_date_in_grid)

    if not events:
        return grid

    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            time = event["start"]
            if first_date_in_grid <= time < tomorrow:
                week = int((time - first_date_in_grid).days // 7)
                day = (time - first_date_in_grid).days % 7
                grid[week][day]["values"][event_list_idx] += event_duration(
                    event,
                )  # assuming event_duration is previously defined

    for absent_list in absents:
        for absent in absent_list:
            start = absent["start"].replace(hour=0, minute=0, second=0, microsecond=0)
            end = absent["end"].replace(hour=0, minute=0, second=0, microsecond=0)
            for absent_day in range((end - start).days + 1):
                absent_date = start + datetime.timedelta(days=absent_day)
                if first_date_in_grid <= absent_date < tomorrow:
                    week = int((absent_date - first_date_in_grid).days // 7)
                    day = (absent_date - first_date_in_grid).days % 7
                    grid[week][day].setdefault("absents", []).append(
                        {"summary": absent["summary"]},
                    )
    return grid


def events_to_array(
    events: list[list[dict[str, Any]]],
    absents: list[list[dict[str, Any]]],
) -> tuple[list[datetime.datetime], list[list[int]]]:
    """Convert list of events to array."""
    date_fmt = "%Y%m%d"
    by_date = {}
    for event_list_idx, event_list in enumerate(events):
        for event in event_list:
            date = event["start"].replace(hour=0, minute=0, second=0, microsecond=0)
            date_str = date.strftime(date_fmt)
            if date_str not in by_date:
                by_date[date_str] = [0 for _ in range(len(events))]
            by_date[date_str][event_list_idx] += event_duration(event)
    # for all absences add days with zeroes to see the gap on plot
    for absent_list in absents:
        for absent in absent_list:
            start = absent["start"].replace(hour=0, minute=0, second=0, microsecond=0)
            end = absent["end"].replace(hour=0, minute=0, second=0, microsecond=0)
            for day in range((end - start).days):
                date = start + datetime.timedelta(days=day)
                date_str = date.strftime(date_fmt)
                if date_str not in by_date:
                    by_date[date_str] = [0 for _ in range(len(events))]
    x = [datetime.datetime.strptime(date_str, date_fmt) for date_str in sorted(by_date.keys())]
    y = [
        [by_date[date_str][event_list_idx] for date_str in sorted(by_date.keys())]
        for event_list_idx in range(len(events))
    ]
    return x, y


def check() -> None:  # pragma: no cover
    """Debug function."""
    from iot_calendar import load_settings  # pylint: disable=import-outside-toplevel,cyclic-import

    settings = load_settings(load_secrets=False)
    print(calendar_events_list(settings, "anna_work_out"))

    from dateutil.tz import tzoffset  # pylint: disable=import-outside-toplevel

    # Set the timezone offset
    three_hour_offset = tzoffset(None, 10800)

    # Set today's date
    calendar_start = datetime.datetime.now(tz=three_hour_offset) - datetime.timedelta(days=25)

    def get_relative_date(
        days_diff: int,
        hour: int,
        minute: int,
        second: int,
    ) -> datetime.datetime:
        return (calendar_start + datetime.timedelta(days=days_diff)).replace(
            hour=hour,
            minute=minute,
            second=second,
            microsecond=0,
        )

    events = [
        [
            {
                "end": get_relative_date(0, 8, 22, 30),
                "start": get_relative_date(0, 8, 15, 39),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(3, 8, 27, 43),
                "start": get_relative_date(3, 8, 16, 35),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(4, 8, 18, 0),
                "start": get_relative_date(4, 8, 12, 9),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(5, 8, 24, 26),
                "start": get_relative_date(5, 8, 17, 8),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(6, 8, 22, 24),
                "start": get_relative_date(6, 8, 16, 34),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(7, 8, 25, 27),
                "start": get_relative_date(7, 8, 20, 26),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(8, 10, 16, 5),
                "start": get_relative_date(8, 10, 10, 7),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(9, 10, 43, 37),
                "start": get_relative_date(9, 10, 38, 45),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(10, 8, 22, 0),
                "start": get_relative_date(10, 8, 14, 47),
                "summary": "Morning work-out",
            },
            {
                "end": get_relative_date(11, 8, 15, 7),
                "start": get_relative_date(11, 8, 10, 58),
                "summary": "Morning work-out",
            },
        ],
        [
            {
                "end": get_relative_date(-1, 20, 23, 0),
                "start": get_relative_date(-1, 20, 3, 5),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(0, 17, 26, 47),
                "start": get_relative_date(0, 16, 55, 56),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(2, 18, 20, 0),
                "start": get_relative_date(2, 17, 48, 0),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(3, 17, 51, 35),
                "start": get_relative_date(3, 17, 28, 31),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(5, 17, 21, 57),
                "start": get_relative_date(5, 16, 49, 55),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(7, 17, 5, 4),
                "start": get_relative_date(7, 16, 26, 51),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(9, 19, 18, 49),
                "start": get_relative_date(9, 18, 58, 12),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(11, 20, 17, 14),
                "start": get_relative_date(11, 20, 3, 25),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(15, 17, 59, 18),
                "start": get_relative_date(26, 17, 36, 51),
                "summary": "Physiotherapy",
            },
            {
                "end": get_relative_date(16, 20, 49, 9),
                "start": get_relative_date(28, 20, 9, 32),
                "summary": "Physiotherapy",
            },
        ],
    ]

    absents: list[list[dict[str, Any]]] = [
        [
            {
                "end": get_relative_date(23, 23, 59, 59),
                "start": get_relative_date(17, 0, 0, 0),
                "summary": "Sick",
            },
        ],
        [],
    ]
    x, y = events_to_array(events, absents)
    pprint.pprint(x)
    pprint.pprint(y)
    grid = events_to_weeks_grid(events, absents)
    pprint.pprint(grid)


if __name__ == "__main__":  # pragma: no cover
    check()
