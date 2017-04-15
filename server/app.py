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
from bson.objectid import ObjectId
import traceback
import datetime
#import mistune


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
            'calendar.html',
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
            (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/')}),
            (r'/styles/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/styles/')}),
            (r'/scripts/(.*)', tornado.web.StaticFileHandler, {'path': os.path.join(os.path.dirname(__file__), 'static/scripts/')})
        ]
        tornado.web.Application.__init__(self, handlers, **settings)


if __name__ == '__main__':
    define("port", default=8080, help="run on the given port", type=int)
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(Application())
    http_server.listen(options.port)

    tornado.ioloop.IOLoop.instance().start()

