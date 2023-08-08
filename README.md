[![Build Status](https://github.com/andgineer/docker-iot-calendar/workflows/ci/badge.svg)](https://github.com/andgineer/docker-iot-calendar/actions)

[Docker Hub container](https://hub.docker.com/r/andgineer/iot-calendar) 
with python http server (Tornado) that generates image for Amazon Kindle.

See [description in my blog](https://sorokin.engineer/posts/en/iot_calendar_synology.html).

The image contains calendar with events from Google Calendar - supposedly events from your IoT
(like [Smart wifi button (Amazon Dash Button hack)](https://sorokin.engineer/posts/en/amazon_dash_button_hack.html)).

Also it has html-page that just serves new version of that image every minute (link to
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

