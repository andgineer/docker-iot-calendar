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
from calendar_image import calendar_image_as_svg
from svg_to_png import svg_to_png
import json
import os.path


SETTINGS_FILE_NAME = '../amazon-dash-private/settings.json'

settings = {}


NO_SETTINGS_FILE = '''\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro'''

def load_settings():
    """ Load settings """
    if not os.path.isfile(SETTINGS_FILE_NAME):
        print(NO_SETTINGS_FILE.format(SETTINGS_FILE_NAME))
        exit(1)
    with open(SETTINGS_FILE_NAME, 'r') as settings_file:
        return json.loads(settings_file.read())


class ImageHandler(tornado.web.RequestHandler):
    def disable_cache(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', '0')
        now = datetime.datetime.now()
        expiration = datetime.datetime(now.year-1, now.month, now.day)
        self.set_header('Last-Modified', expiration)

    #todo async decorators and calls to API
    def get(self):
        # with open('static/img/ancient_scholar.png', 'rb') as image_file:
        #     image = image_file.read()
        image = svg_to_png(calendar_image_as_svg())
        self.write(image)
        self.flush()


class CalendarHandler(tornado.web.RequestHandler):
    def disable_cache(self):
        self.set_header('Cache-Control', 'no-cache, must-revalidate')
        self.set_header('Expires', '0')
        now = datetime.datetime.now()
        expiration = datetime.datetime(now.year-1, now.month, now.day)
        self.set_header('Last-Modified', expiration)

    #todo async decorators and calls to API
    def get(self):
        self.disable_cache()
        self.render(
            'index.html',
            page_title='Calendar',
        )


class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            debug=True,
        )
        handlers = [
            (r'/', CalendarHandler),
            (r'/page_image.png', ImageHandler),
            (r'/img/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/img')}),
            (r'/styles/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/styles/')}),
            (r'/scripts/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/scripts/')})
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    settings = load_settings()

    define('port', default=4444, help='run on the given port', type=int)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)
    print('Running on port {}'.format(options.port))

    tornado.ioloop.IOLoop.instance().start()
