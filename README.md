Server generate image with calendar (page_image.png) for Amazon Kindle.
Also it has html-page (index.html) that just serves that page with new version of image every 10 seconds.

Calendar contains events from Google Calendar - supposedly events from your IoT
(like [Smart wifi button (Amazon Dash Button hack)](http://masterandrey.com/posts/en/amazon_dash_button_hack/)).

I draw image in svg with 
[svgwrite](http://svgwrite.readthedocs.io/en/master/attributes/presentation.html),
and convert it into png with [cairosvg](http://cairosvg.org/documentation/).

It look like crazy overkill but in future I could add some interactions (use svg itself inside html).
And I can use vector images.

To install system dependencies for cairosvg in OSX (MacOS):
'''
brew update
brew install cairo
'''
