# -*- coding: utf-8 -*-
""" Web-server for calendar
"""

import tornado.ioloop
import tornado.web
import logging
import os
import os.path
import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
import pprint
import json
from tornado.escape import json_encode
import datetime
from calendar_image import draw_calendar, ImageParams
from calendar_data import events_to_weeks_grid, events_to_array, calendar_events_list, dashboard_absent_events_list
from google_calendar import collect_events, GOOGLE_CREDENTIALS_PARAM
from openweathermap_org import Weather, WEATHER_KEY_PARAM
import json
import os.path


SETTINGS_FILE_NAME = '../amazon-dash-private/settings.json'

settings = {}


NO_SETTINGS_FILE = '''\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro'''

def load_settings(secrets_folder=None):
    """ Load settings """
    def set_folder(params, substr, folder):
        for param in params:
            if param.find(substr) > -1:
                _, name = os.path.split(params[param])
                params[param] = os.path.join(folder, name)

    if not os.path.isfile(SETTINGS_FILE_NAME):
        print(NO_SETTINGS_FILE.format(SETTINGS_FILE_NAME))
        exit(1)
    with open(SETTINGS_FILE_NAME, 'r', encoding='utf-8-sig') as settings_file:
        settings = json.loads(settings_file.read())

    if secrets_folder:
        g_path, g_name = os.path.split(settings[GOOGLE_CREDENTIALS_PARAM])
        settings[GOOGLE_CREDENTIALS_PARAM] = os.path.join(secrets_folder, g_name)
        w_path, w_name = os.path.split(settings[WEATHER_KEY_PARAM])
        settings[WEATHER_KEY_PARAM] = os.path.join(secrets_folder, w_name)
    if 'images_folder' in settings:
        images_folder = settings['images_folder']
        for dashboard in settings['dashboards']:
            set_folder(settings['dashboards'][dashboard], 'image', images_folder)
            if 'absent' in settings['dashboards'][dashboard]:
                for absent_event in settings['dashboards'][dashboard]['absent']:
                    set_folder(absent_event, 'image', images_folder)
        for button in settings['actions']:
            if 'summary' in settings['actions'][button]:
                for summary in settings['actions'][button]['summary']:
                    set_folder(summary, 'image', images_folder)
            for action in settings['actions'][button]['actions']:
                set_folder(action, 'image', images_folder)
    print('Processed settings:')
    pprint.pprint(settings)
    print()
    return settings


class HandlerWithParams(tornado.web.RequestHandler):
    def load_params(self, **kw):
        defaults = ImageParams(
            dashboard=kw.get('dashboard', ''),
            format=kw.get('format', 'gif'),
            style='grayscale',
            xkcd=1,
            rotate=90
        )
        params = [self.get_argument(param, self.get_argument(param[0], getattr(defaults, param))) for param in ImageParams._fields]
        return ImageParams(*params)

    def disable_cache(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', '0')
        now = datetime.datetime.now()
        expiration = datetime.datetime(now.year-1, now.month, now.day)
        self.set_header('Last-Modified', expiration)


class DashboardImageHandler(HandlerWithParams):
    #todo async decorators and async version of draw_calendar
    def get(self, image_format):
        self.disable_cache()
        params = self.load_params(format=image_format, dashboard=list(settings['dashboards'].keys())[0])
        calendar_events = calendar_events_list(settings, params.dashboard)
        absent_events = dashboard_absent_events_list(settings, 'anna_work_out')
        events, absents = collect_events(calendar_events, absent_events, settings)
        grid = events_to_weeks_grid(events, absents)
        x, y = events_to_array(events, absents)
        wth = Weather(settings)
        weather = wth.get_weather(settings['latitude'], settings['longitude'])
        if weather:
            weather['images_folder'] = settings['images_folder']
        dashboard = settings['dashboards'][params.dashboard]
        if 'images_folder' not in dashboard:
            dashboard['images_folder'] = settings['images_folder']
        image = draw_calendar(
            grid,
            x, y,
            weather,
            dashboard,
            calendar_events,
            absent_events,
            params
        )
        self.write(image)
        self.set_header("Content-type",  "image/{}".format(format))
        self.flush()


class DashboardListHandler(HandlerWithParams):
    def get(self):
        self.disable_cache()
        params = self.load_params()
        if params.dashboard:
            self.render(
                'dashboard.html',
                dashboard_name=params.dashboard,
                style=params.style,
                xkcd=params.xkcd,
                format=params.format,
                rotate=params.rotate,
                page_title='Dashboard',
            )
        else:
            dashboards = settings['dashboards']
            self.render(
                'index.html',
                dashboards=dashboards,
                page_title='Dashboards list',
            )


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            debug=True,
        )
        handlers = [
            (r'/', DashboardListHandler),
            (r'/index.html', DashboardListHandler),
            (r'/dashboard\.(\w*)', DashboardImageHandler),
            (r'/d\.(\w*)', DashboardImageHandler),
            (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/img')}),
            (r'/styles/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/styles/')}),
            (r'/scripts/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/scripts/')})
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':  # pragma: no cover
    define('port', default=4444, help='run on the given port', type=int)
    define('secrets', default=None, help='path to files with secrets', type=str)
    tornado.options.parse_command_line()
    settings = load_settings(options.secrets)
    http_server = tornado.httpserver.HTTPServer(Application())
    print('Running on port {}'.format(options.port))
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()
