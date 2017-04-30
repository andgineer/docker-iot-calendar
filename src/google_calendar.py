"""Load events from Google Calendar using Google Calendar API """

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import httplib2
import datetime
import os
import os.path
import dateutil.parser
import time
from pprint import pprint
from cached_decorator import cached
import dateutil.tz


GOOGLE_CREDENTIALS_PARAM = 'credentials_file_name'
MIN_GOOGLE_API_CALL_DELAY_SECONDS = 15

class Calendar(object):
    def __init__(self, settings, calendar_id):
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.tz = os.environ.get('TZ', 'Europe/Moscow')
        self.calendarId = calendar_id

    def get_credentials_http(self):
        if not os.path.isfile(self.settings[GOOGLE_CREDENTIALS_PARAM]):
            print('''Google API credentials file {} not found.
Get it on https://console.developers.google.com/start/api?id=calendar'''.format(
                self.settings[GOOGLE_CREDENTIALS_PARAM]
            ))
            return None
        try:
            credentials = ServiceAccountCredentials.from_json_keyfile_name(
                self.settings[GOOGLE_CREDENTIALS_PARAM],
                [
                    'https://www.googleapis.com/auth/calendar'
                ]
            )
        except Exception as e:
            print('''Cannot login to Google API - check your credential file {}.
You can get new one from https://console.developers.google.com/start/api?id=calendar'''.format(
                self.settings[GOOGLE_CREDENTIALS_PARAM]
            ))
            return None
        return credentials.authorize(httplib2.Http())

    def get_service(self):
        if not self.http:
            return None
        #logging.getLogger('googleapiclient.discovery').setLevel(logging.CRITICAL)
        return discovery.build(
            'calendar',
            'v3',
            http=self.http,
            cache_discovery=False # file cash bug: https://github.com/google/google-api-python-client/issues/299
            # also we can use older pip uninstall oauth2client ; pip install oauth2client==3.0.0
        )

    def parse_time(self, s):
        return dateutil.parser.parse(s)

    def time_to_str(self, t):
        GCAL_TIME_FORMAT = '%Y-%m-%dT%H:%M:%S'
        tz = - time.timezone / 60 / 60 * 100
        #todo that is incorrect - you need minutes after ':' not hours % 100
        # so h = int(- time.timezone / 60 / 60)
        # m = abs(time.timezone / 60) - h * 60
        s = t.strftime(GCAL_TIME_FORMAT) + '%+03d:%02d' % (tz / 100, abs(tz % 100))
        return s

    def get_last_events(self, summary, days=31):
        """
        :param summary: text to search
        :param days: days from today to collect events
        :return:
        [ {'summary': summary, 'start': start, 'end': end} ]
        """
        result = []
        if not self.service:
            return result
        tzinfo = dateutil.tz.tzoffset(None, -time.timezone)
        page_token = None
        while True:
            events = self.service.events().list(
                calendarId=self.calendarId,
                timeMin=self.google_time_format(datetime.datetime.now() - datetime.timedelta(days=days)),
                q=summary,
                #timeZone='UTC',
                orderBy="startTime",
                singleEvents=True,
                showDeleted=False,
                pageToken=page_token
            ).execute()
            if len(events['items']) > 0:
                for event in events['items']:
                    if 'dateTime' in event['start']:
                        start = self.parse_time(event['start']['dateTime'])
                    else:
                        start = self.parse_time(event['start']['date']).replace(tzinfo=tzinfo)
                    if 'dateTime' in event['end']:
                        end = self.parse_time(event['end']['dateTime'])
                    else:
                        end = self.parse_time(event['end']['date']).replace(tzinfo=tzinfo) - datetime.timedelta(seconds=1)
                    result.append({'summary': event['summary'], 'start': start, 'end': end})
            page_token = events.get('nextPageToken')
            if not page_token:
                return result

    def google_time_format(self, t):
        return t.strftime('%Y-%m-%dT%H:%M:%SZ')

    def google_now(self):
        return self.google_time_format(datetime.datetime.now())

    def google_today(self):
        return self.google_time_format(
            datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        )

@cached(
    cache_time_seconds=MIN_GOOGLE_API_CALL_DELAY_SECONDS,
    print_if_cached='Use stored google calendar data (from {time})'
)
def collect_events(calendar_events, absent_events, settings):
    calendars = {}
    events = []
    absents = []
    for event in calendar_events:
        if event['calendar_id'] in calendars:
            calendar_processed = True
        else:
            calendar_processed = False
            calendars[event['calendar_id']] = Calendar(settings, event['calendar_id'])
        calendar = calendars[event['calendar_id']]
        events.append(calendar.get_last_events(event['summary']))
        if not calendar_processed:
            for event in absent_events:
                absents.append(calendar.get_last_events(event['summary']))
    return events, absents


if __name__ == "__main__":
    from iot_calendar import load_settings
    from calendar_data import calendar_events_list, dashboard_absent_events_list
    settings = load_settings(secrets_folder='../secrets')
    calendar_events = calendar_events_list(settings, 'anna_work_out')
    absent_events = dashboard_absent_events_list(settings, 'anna_work_out')
    pprint(absent_events)
    events, absents = collect_events(calendar_events, absent_events, settings)
    pprint(events)
    pprint(absents)
