"use strict";

/*
updatePageImage gets the newest version of the
image from the server. To prevent the browser from loading
a cached version of the image, we add a query to the URL 
for the image. We're using the time, but any query that is
guaranteed not to repeat would be fine.
*/
function updatePageImage() {
    var d = new Date();
	//For some reason, the getTime() function made the Kindle browser quit after a few minutes. Changing this to getSeconds() seems fixed the problem...
	$("#page_image").attr("src", "dashboard.png?b={{ dashboard_name }}&style={{ style }}&xkcd={{ xkcd }}&format={{ format }}&_d=" + d.getSeconds());
}

$(document).ready(function () {
    //setInterval calls every ... ms
    setInterval(updatePageImage, 60000);
});
