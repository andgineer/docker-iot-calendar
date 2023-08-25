[![Build Status](https://github.com/andgineer/docker-iot-calendar/workflows/ci/badge.svg)](https://github.com/andgineer/docker-iot-calendar/actions)[![Coverage](https://raw.githubusercontent.com/andgineer/docker-iot-calendar/python-coverage-comment-action-data/badge.svg)](https://htmlpreview.github.io/?https://github.com/andgineer/docker-iot-calendar/blob/python-coverage-comment-action-data/htmlcov/index.html)

[Docker Hub container](https://hub.docker.com/r/andgineer/iot-calendar)
that generates image for Amazon Kindle.

![calendar](docs/include/calendar.png)
See [description in my blog](https://sorokin.engineer/posts/en/iot_calendar_synology.html).

The image contains calendar with events from Google Calendar - supposedly events from your IoT
(like [Smart wifi button (Amazon Dash Button hack)](https://sorokin.engineer/posts/en/amazon_dash_button_hack.html)).

Also it has html-page that updates the image every minute (link to
this page in index.html).

Run in the `docker-iot-calendar` folder:
```
docker run --rm -it -v $PWD/amazon-dash-private:/amazon-dash-private:ro -p 4444:4444 andgineer/iot-calendar
```

Local address for the calendar page `http://localhost:4444`

At first I thought it would be great idea to use
[svgwrite](http://svgwrite.readthedocs.io/en/master/attributes/presentation.html),
and [cairosvg](http://cairosvg.org/documentation/), but then decided otherwise
and use [matplotlib](http://matplotlib.org) instead.

To install system dependencies in Mac OSX (if you want to run it outside docker container):
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
As HTTP server I use [tornado](http://www.tornadoweb.org/en/stable/).


# Performance

https://andgineer.github.io/docker-iot-calendar/dev/bench
