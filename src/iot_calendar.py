# -*- coding: utf-8 -*-
"""Web-server for calendar."""
import datetime
import json
import os
import os.path
import pprint
import sys
from pathlib import Path
from typing import Any, Awaitable, Dict, Optional, Sequence, Tuple, Union, cast

import tornado.auth
import tornado.escape
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from tornado.options import define, options
from tornado.routing import _RuleList

from calendar_data import (
    calendar_events_list,
    dashboard_absent_events_list,
    events_to_array,
    events_to_weeks_grid,
)
from calendar_image import ImageParams, draw_calendar
from google_calendar import GOOGLE_CREDENTIALS_PARAM, collect_events
from openweathermap_org import WEATHER_KEY_PARAM, Weather

SETTINGS_FOLDER = "../amazon-dash-private"
SETTINGS_FILE_NAME = "settings.json"

settings: Dict[str, Any] = {}


NO_SETTINGS_FILE = """\nNo {} found. \nIf you run application in docker container you
should connect volume with setting files, like
    -v $PWD/amazon-dash-private:/amazon-dash-private:ro"""


def load_settings(folder: Optional[str] = None, load_secrets: bool = True) -> Dict[str, Any]:
    """Load settings."""

    def set_folder(params: Dict[str, Any], substr: str, folder: str) -> None:
        """Add folder to params if substr is in the param name."""
        for param in params:
            if param.find(substr) > -1:
                _, name = os.path.split(params[param])
                params[param] = os.path.join(folder, name)

    if folder is None:
        folder = SETTINGS_FOLDER
    settings_path = Path(os.path.join(folder, SETTINGS_FILE_NAME))
    if not settings_path.is_file():
        print(NO_SETTINGS_FILE.format(settings_path))
        sys.exit(1)
    result: Dict[str, Any] = json.loads(settings_path.read_text(encoding="utf-8-sig"))

    if load_secrets:
        g_path, g_name = os.path.split(result[GOOGLE_CREDENTIALS_PARAM])
        result[GOOGLE_CREDENTIALS_PARAM] = os.path.join(folder, g_name)
        w_path, w_name = os.path.split(result[WEATHER_KEY_PARAM])
        result[WEATHER_KEY_PARAM] = os.path.join(folder, w_name)
    if "images_folder" in result:
        images_folder = result["images_folder"]
        for dashboard in result["dashboards"]:
            set_folder(result["dashboards"][dashboard], "image", images_folder)
            if "absent" in result["dashboards"][dashboard]:
                for absent_event in result["dashboards"][dashboard]["absent"]:
                    set_folder(absent_event, "image", images_folder)
        for button in result["events"]:
            if "summary" in result["events"][button] and isinstance(
                result["events"][button]["summary"], list
            ):
                for summary in result["events"][button]["summary"]:
                    set_folder(summary, "image", images_folder)
            for action in result["events"][button]["actions"]:
                set_folder(action, "image", images_folder)
    print("Processed settings:")
    pprint.pprint(result)
    print()
    return result


class HandlerWithParams(tornado.web.RequestHandler):  # type: ignore
    """Handler with params."""

    def load_params(self, **kw: Any) -> ImageParams:
        """Load params from request."""
        defaults = ImageParams(
            dashboard=kw.get("dashboard", ""),
            format=kw.get("format", "png"),
            style="grayscale",
            xkcd=1,
            rotate=90,
        )
        params = [
            self.get_argument(param, self.get_argument(param[0], getattr(defaults, param)))
            for param in ImageParams._fields
        ]
        return ImageParams(*params)

    def disable_cache(self) -> None:
        """Disable cache."""
        self.set_header("Cache-Control", "no-cache, must-revalidate")
        self.set_header("Expires", "0")
        now = datetime.datetime.now()
        expiration = datetime.datetime(now.year - 1, now.month, now.day)
        self.set_header("Last-Modified", expiration)

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """Receive data."""


class DashboardImageHandler(HandlerWithParams):
    """Dashboard image handler."""

    # todo async decorators and async version of draw_calendar
    def get(self, image_format: str) -> None:
        """Get image."""
        self.disable_cache()
        params = self.load_params(
            format=image_format, dashboard=list(settings["dashboards"].keys())[0]
        )
        calendar_events = calendar_events_list(settings, params.dashboard)
        absent_events = dashboard_absent_events_list(settings, "anna_work_out")
        events, absents = collect_events(calendar_events, absent_events, settings)
        grid = events_to_weeks_grid(events, absents)
        x, y = events_to_array(events, absents)
        wth = Weather(settings)
        weather = wth.get_weather(settings["latitude"], settings["longitude"])
        if weather:
            weather.images_folder = settings["images_folder"]
        dashboard = settings["dashboards"][params.dashboard]
        if "images_folder" not in dashboard:
            dashboard["images_folder"] = settings["images_folder"]
        image = draw_calendar(
            grid, x, y, weather, dashboard, calendar_events, absent_events, params
        )
        self.write(image)
        self.set_header("Content-type", f"image/{image_format}")
        self.flush()

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """Receive data."""


class DashboardListHandler(HandlerWithParams):
    """Dashboard list handler."""

    def get(self) -> None:
        """Get list of dashboards."""
        self.disable_cache()
        params = self.load_params()
        if params.dashboard:
            self.render(
                "dashboard.html",
                dashboard_name=params.dashboard,
                style=params.style,
                xkcd=params.xkcd,
                format=params.format,
                rotate=params.rotate,
                page_title="Dashboard",
            )
        else:
            dashboards = settings["dashboards"]
            self.render(
                "index.html",
                dashboards=dashboards,
                page_title="Dashboards list",
            )

    def data_received(self, chunk: bytes) -> Optional[Awaitable[None]]:
        """Receive data."""


HandlersType = Optional[
    Sequence[
        Union[
            Tuple[str, type[HandlerWithParams]],
            Tuple[str, type[tornado.web.StaticFileHandler], Dict[str, Any]],
        ]
    ]
]


class Application(tornado.web.Application):  # type: ignore
    """Application."""

    def __init__(
        self,
        server_settings: Optional[Dict[str, Any]] = None,
        handlers: HandlersType = None,
    ):
        """Init."""
        if server_settings is None:
            server_settings = {
                "template_path": os.path.join(os.path.dirname(__file__), "../templates"),
                "debug": True,
            }
        if handlers is None:
            handlers = [
                (r"/", DashboardListHandler),
                (r"/index.html", DashboardListHandler),
                (r"/dashboard\.(\w*)", DashboardImageHandler),
                (r"/d\.(\w*)", DashboardImageHandler),
                (
                    r"/img/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": os.path.join(os.path.dirname(__file__), "../static/img")},
                ),
                (
                    r"/styles/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": os.path.join(os.path.dirname(__file__), "../static/styles/")},
                ),
                (
                    r"/scripts/(.*)",
                    tornado.web.StaticFileHandler,
                    {"path": os.path.join(os.path.dirname(__file__), "../static/scripts/")},
                ),
            ]
        tornado.web.Application.__init__(self, cast(_RuleList, handlers), **server_settings)


def main() -> None:  # pragma: no cover
    """Check."""
    global settings  # pylint: disable=global-statement

    define("port", default=4444, help="run on the given port", type=int)
    define("folder", default=None, help="path to settings and files with secrets", type=str)
    tornado.options.parse_command_line()

    settings = load_settings(folder=options.folder)
    http_server = tornado.httpserver.HTTPServer(Application())
    print(f"Running on port {options.port}")

    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":  # pragma: no cover
    main()
