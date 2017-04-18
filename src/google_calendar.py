"""Load events from Google Calendar using Google Calendar API """

from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient import discovery
import httplib2
import datetime
import os
import dateutil.parser
import time
from pprint import pprint


class Calendar(object):
    def __init__(self, settings, calendar_id):
        self.settings = settings
        self.http = self.get_credentials_http()
        self.service = self.get_service()
        self.tz = os.environ.get('TZ', 'Europe/Moscow')
        self.calendarId = calendar_id

    def get_credentials_http(self):
        credentials = ServiceAccountCredentials.from_json_keyfile_name(
            self.settings['credentials_file_name'],
            [
                'https://www.googleapis.com/auth/calendar'
            ]
        )
        return credentials.authorize(httplib2.Http())

    def get_service(self):
        return discovery.build(
            'calendar',
            'v3',
            http=self.http
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
                    start = self.parse_time(event['start']['dateTime'])
                    end = self.parse_time(event['end']['dateTime'])
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


def collect_events():
    events = []
    for button in settings['actions']:
        for action in settings['actions'][button]['actions']:
            if action['type'] == 'calendar':
                calendar = Calendar(settings, action['calendar_id'])
                events.extend(calendar.get_last_events(button))
    return events


if __name__ == "__main__":
    from app import load_settings
    settings = load_settings()

    events = collect_events()
    pprint(events)
