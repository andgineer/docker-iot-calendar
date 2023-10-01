"""Load events from Google Calendar using Google Calendar API."""

import datetime
import os
import os.path
import time
from datetime import timedelta
from pprint import pprint
from typing import Any, Dict, List, Optional, Tuple

import dateutil.parser
import dateutil.tz
import httplib2
from googleapiclient import discovery
from oauth2client.service_account import ServiceAccountCredentials

from cached_decorator import cached

GOOGLE_CREDENTIALS_PARAM = "credentials_file_name"
MIN_GOOGLE_API_CALL_DELAY_SECONDS = 15


class Calendar:
    """Google Calendar API wrapper."""

    def __init__(self, settings: Dict[str, Any], calendar_id: str) -> None:
        """Init."""
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.tz = os.environ.get("TZ", "Europe/Moscow")
        self.calendarId = calendar_id

    def get_credentials_http(self) -> Optional[httplib2.Http]:
        """Get credentials."""
        if GOOGLE_CREDENTIALS_PARAM not in self.settings:
            raise ValueError(f"'{GOOGLE_CREDENTIALS_PARAM}' not found in settings.")

        if not os.path.isfile(self.settings[GOOGLE_CREDENTIALS_PARAM]):
            print(
                f"""Google API credentials file {self.settings[GOOGLE_CREDENTIALS_PARAM]} not found.
Get it on https://console.developers.google.com/start/api?id=calendar"""
            )
            return None
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.settings[GOOGLE_CREDENTIALS_PARAM],
                ["https://www.googleapis.com/auth/calendar"],
            )
        except Exception:
            print(
                f"""Cannot login to Google API - check your credential file {self.settings[GOOGLE_CREDENTIALS_PARAM]}.
You can get new one from https://console.developers.google.com/start/api?id=calendar"""
            )
            return None
        return credentials.authorize(httplib2.Http())

    def get_service(self) -> Optional[discovery.Resource]:
        """Get service."""
        if not self.http:
            return None
        # logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)
        return discovery.build(
            "calendar",
            "v3",
            http=self.http,
            cache_discovery=False  # file cash bug: https://github.com/google/google-api-python-client/issues/299
            # also we can use older pip uninstall oauth2client ; pip install oauth2client==3.0.0
        )

    def parse_time(self, s: str) -> datetime.datetime:
        """Parse time."""
        return dateutil.parser.parse(s)

    def time_to_str(self, t: datetime.datetime) -> str:
        """Time to string."""
        GCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        minutes = -time.timezone // 60
        return f"{t.strftime(GCAL_TIME_FORMAT)}{minutes // 60:+03d}:{abs(minutes % 60):02d}"

    def get_last_events(
        self, summary: str, days: int = 31, default_length: int = 900
    ) -> List[Dict[str, Any]]:
        """Get last events.

        :param summary: text to search
        :param days: days from today to collect events
        :default_length: default length of event in seconds
        :return:
        [ {'summary': summary, 'start': start, 'end': end} ]
        """

        def get_event_interval(
            event: Dict[str, Any]
        ) -> Tuple[datetime.datetime, datetime.datetime]:
            """Get event interval.

            :param event: with ['start'] and ['end']
            :return: start and end calculated from dateTime or date formats of google calendar
            """

            def get_timepoint(timepoint: Dict[str, Any]) -> datetime.datetime:
                """Get timepoint."""
                if "dateTime" in timepoint:
                    return self.parse_time(timepoint["dateTime"])
                return self.parse_time(timepoint["date"]).replace(tzinfo=tzinfo)

            start = get_timepoint(event["start"])
            end = get_timepoint(event["end"])
            if start == end:
                end = start + timedelta(seconds=default_length)
            return start, end

        result: List[Dict[str, Any]] = []
        if not self.service:
            return result
        tzinfo = dateutil.tz.tzoffset(None, -time.timezone)
        page_token = None
        while True:
            events = (
                self.service.events()
                .list(
                    calendarId=self.calendarId,
                    timeMin=self.google_time_format(
                        datetime.datetime.now() - datetime.timedelta(days=days)
                    ),
                    q=summary,
                    # timeZone='UTC',
                    orderBy="startTime",
                    singleEvents=True,
                    showDeleted=False,
                    pageToken=page_token,
                )
                .execute()
            )
            if len(events["items"]) > 0:
                for event in events["items"]:
                    start, end = get_event_interval(event)
                    result.append({"summary": event["summary"], "start": start, "end": end})
            page_token = events.get("nextPageToken")
            if not page_token:
                return result

    def google_time_format(self, t: datetime.datetime) -> str:
        """Google time format."""
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def google_now(self) -> str:
        """Google now."""
        return self.google_time_format(datetime.datetime.now())

    def google_today(self) -> str:
        """Google today."""
        return self.google_time_format(
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )


@cached(
    seconds=MIN_GOOGLE_API_CALL_DELAY_SECONDS,
    trace_fmt="Use stored google calendar data (from {time})",
)
def collect_events(
    calendar_events: List[Dict[str, Any]],
    absent_events: List[Dict[str, Any]],
    settings: Dict[str, Any],
) -> Tuple[List[List[Dict[str, Any]]], List[List[Dict[str, Any]]]]:
    """Collect events.

    Return (events, absents)
    For each event from `calendar_events` add to events list of events from Google Calendar.
    And to absents list of events from Google Calendar with summary from `absent_events`.
    """
    calendars = {}
    events = []
    absents: List[List[Dict[str, Any]]] = []
    for event in calendar_events:
        if event["calendar_id"] in calendars:
            calendar_processed = True
        else:
            calendar_processed = False
            calendars[event["calendar_id"]] = Calendar(settings, event["calendar_id"])
        calendar = calendars[event["calendar_id"]]
        events.append(
            calendar.get_last_events(event["summary"], default_length=event.get("default", 900))
        )
        if not calendar_processed:
            absents.extend(calendar.get_last_events(event["summary"]) for event in absent_events)
    return events, absents


def check() -> None:  # pragma: no cover
    """Check."""
    from calendar_data import (  # pylint: disable=import-outside-toplevel
        calendar_events_list,
        dashboard_absent_events_list,
    )
    from iot_calendar import load_settings  # pylint: disable=import-outside-toplevel,cyclic-import

    settings = load_settings()
    calendar_events = calendar_events_list(settings, "anna_work_out")
    absent_events = dashboard_absent_events_list(settings, "anna_work_out")
    pprint(absent_events)
    events, absents = collect_events(calendar_events, absent_events, settings)
    print("=" * 20, "events")
    pprint(events)
    print("=" * 20, "absents")
    pprint(absents)


if __name__ == "__main__":  # pragma: no cover
    check()
