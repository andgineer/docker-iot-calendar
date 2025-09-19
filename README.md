[![Build Status](https://github.com/andgineer/docker-iot-calendar/workflows/ci/badge.svg)](https://github.com/andgineer/docker-iot-calendar/actions)
[![Coverage](https://raw.githubusercontent.com/andgineer/docker-iot-calendar/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)
[![Docker Automated build](https://img.shields.io/docker/image-size/andgineer/iot-calendar)](https://hub.docker.com/r/andgineer/iot-calendar)

[Docker Hub container](https://hub.docker.com/r/andgineer/iot-calendar)
that generates calendar images for Amazon Kindle.

![calendar](docs/src/en/images/calendar.png)

The image displays a calendar with events from Google Calendar - typically events from your IoT devices
(like [Smart wifi button (Amazon Dash Button hack)](https://sorokin.engineer/posts/en/amazon_dash_button_hack.html)).

You can point your Kindle browser to an HTML page that updates the image every minute,
so you can view the calendar on your Kindle.

## Usage
Read [description in my blog](https://sorokin.engineer/posts/en/iot_calendar_synology.html).

## Prepare environment
A detailed manual on how to create Google and OpenWeather credentials is in the blog post mentioned above.

Setup steps:
* Create Google project
* Create Google service account
* Enable [Google Calendar API](https://console.cloud.google.com/apis/api/calendar-json.googleapis.com/metrics)
* [Create key](https://console.cloud.google.com/iam-admin/serviceaccounts/details/110121235683045242579;edit=true/keys) -> Add Key -> JSON
* Replace `amazon-dash-hack.json` in `amazon-dash-private` folder with downloaded file
* Create Google calendar where your IoT device will publish events (like [Amazon Dash Button](https://sorokin.engineer/posts/en/amazon_dash_button_hack.html))
* Share Google calendar with service account
* Create OpenWeatherMap API key and place it into `amazon-dash-private/openweathermap.key` file


## Local run

Prepare secrets as described in the blog post mentioned above.

Copy the `amazon-dash-private` folder up one level, so it's in the same folder as the `docker-iot-calendar` project.
Place your secrets in this folder copy.

Run in the `docker-iot-calendar` folder:
```
make run
```

Local address for the calendar page: `http://localhost:4444`

## Development

### Packages

At first I thought it would be great idea to use
[svgwrite](http://svgwrite.readthedocs.io/en/master/attributes/presentation.html),
and [cairosvg](http://cairosvg.org/documentation/), but then decided otherwise
and use [matplotlib](http://matplotlib.org) instead.

### Development dependencies

To install system dependencies on macOS (if you want to run it outside Docker container):
```
brew update
brew install cairo
```

### Matplotlib fonts

You have to install [Humor font](http://antiyawn.com/uploads/humorsans.html),
[xkcd font](https://github.com/ipython/xkcd-font) or [xkcd font](https://github.com/andgineer/docker-matplotlib/blob/master/xkcd.otf)
and [Comic Neue](https://fonts.google.com/specimen/Comic+Neue).

If you already had matplotlib installed, after font installation you have to remove `~/.matplotlib/fontList.json`.

### HTTP server

The application uses [Tornado](http://www.tornadoweb.org/en/stable/) as the HTTP server.

### Local debug

Create and/or activate virtual environment (note two dots):

    . ./activate.sh

Now you can run debug code or debug the application, for example:

    python src/iot_calendar.py

## Performance

https://andgineer.github.io/docker-iot-calendar/builds/benchmark

## Coverage reports
* [Codecov](https://app.codecov.io/gh/andgineer/docker-iot-calendar/tree/master/src)
* [Coveralls](https://coveralls.io/github/andgineer/docker-iot-calendar)
