Server generate image with calendar (page_image.png) for Amazon Kindle.
Also it has html-page (index.html) that just serves that page with new version of image every 10 seconds.

Calendar contains events from Google Calendar - supposedly events from your IoT
(like [Smart wifi button (Amazon Dash Button hack)](http://masterandrey.com/posts/en/amazon_dash_button_hack/)).

Run in the `docker-iot-calendar` folder:
```
docker run --rm -it -v $PWD/amazon-dash-private:/amazon-dash-private:ro -p 4444:4444 masterandrey/docker-iot-calendar
```

Local address for the calendar page `http://localhost:4444`

At first I thought it would be great idea to use
[svgwrite](http://svgwrite.readthedocs.io/en/master/attributes/presentation.html),
and [cairosvg](http://cairosvg.org/documentation/), but then decided otherwise.

But if you do need cairosvg, to install system dependencies in OSX (if you want to run it outside docker container):
'''
brew update
brew install cairo
'''
