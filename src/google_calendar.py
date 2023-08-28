"""Load events from Google Calendar using Google Calendar API."""

import datetime
import os
import os.path
import time
from datetime import timedelta
from pprint import pprint

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

    def __init__(self, settings, calendar_id):
        """Init."""
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.tz = os.environ.get("TZ", "Europe/Moscow")
        self.calendarId = calendar_id

    def get_credentials_http(self):
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

    def get_service(self):
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

    def parse_time(self, s):
        """Parse time."""
        return dateutil.parser.parse(s)

    def time_to_str(self, t):
        """Time to string."""
        GCAL_TIME_FORMAT = "%Y-%m-%dT%H:%M:%S"
        tz = -time.timezone / 60 / 60 * 100
        # todo that is incorrect - you need minutes after ':' not hours % 100
        # so h = int(- time.timezone / 60 / 60)
        # m = abs(time.timezone / 60) - h * 60
        s = t.strftime(GCAL_TIME_FORMAT) + "%+03d:%02d" % (tz / 100, abs(tz % 100))
        return s

    def get_last_events(self, summary, days=31, default_length=900):
        """Get last events.

        :param summary: text to search
        :param days: days from today to collect events
        :return:
        [ {'summary': summary, 'start': start, 'end': end} ]
        """

        def get_event_interval(event):
            """Get event interval.

            :param event: with ['start'] and ['end']
            :return: start and end calculated from dateTime or date formats of google calendar
            """

            def get_timepoint(timepoint):
                """Get timepoint."""
                if "dateTime" in timepoint:
                    return self.parse_time(timepoint["dateTime"])
                return self.parse_time(timepoint["date"]).replace(tzinfo=tzinfo)

            start = get_timepoint(event["start"])
            end = get_timepoint(event["end"])
            if start == end:
                end = start + timedelta(seconds=default_length)
            return start, end

        result = []
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

    def google_time_format(self, t):
        """Google time format."""
        return t.strftime("%Y-%m-%dT%H:%M:%SZ")

    def google_now(self):
        """Google now."""
        return self.google_time_format(datetime.datetime.now())

    def google_today(self):
        """Google today."""
        return self.google_time_format(
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )


@cached(
    seconds=MIN_GOOGLE_API_CALL_DELAY_SECONDS,
    trace_fmt="Use stored google calendar data (from {time})",
)
def collect_events(calendar_events, absent_events, settings):
    """Collect events."""
    calendars = {}
    events = []
    absents = []
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
            for event in absent_events:
                absents.append(calendar.get_last_events(event["summary"]))
    return events, absents


if __name__ == "__main__":  # pragma: no cover
    from .calendar_data import calendar_events_list, dashboard_absent_events_list
    from .iot_calendar import load_settings

    settings = load_settings(secrets_folder="../secrets")
    calendar_events = calendar_events_list(settings, "anna_work_out")
    absent_events = dashboard_absent_events_list(settings, "anna_work_out")
    pprint(absent_events)
    events, absents = collect_events(calendar_events, absent_events, settings)
    pprint(events)
    pprint(absents)
