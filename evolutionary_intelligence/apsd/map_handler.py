import urllib


def get_google_map(imgDir, center=None, imgSize=(640, 480), imgFormat="png",
                   zoom=15, mapType="satellite", markers=None):
    """
    retrieve a map (image) from the static google maps server
    (http://hci574.blogspot.com.tr/2010/04/using-google-maps-static-images.html)
    (http://code.google.com/apis/maps/documentation/staticmaps/)

    creates a request string with a URL like this:
    http://maps.google.com/maps/api/staticmap?center=Brooklyn+Bridge,New+York,NY&zoom=14&size=512x512
    &maptype=roadmap&markers=color:blue|label:S|40.702147,-74.015794&sensor=false

    :param
        imgDir (string)     - retrieving image will save to file to this directory
        imgSize (int tuple) - map width and height values for retrieving from google map
        imgFormat (string)  - image file type (default png)
        zoom (integer)      - retrieving map area zoom ratio
        mapType (string)    - retrieving map type (default satellite (roadmap, hybrid, terrain))

    :return
        saved map image file from retrieving google map
    """

    request = "http://maps.google.com/maps/api/staticmap?"

    if center is not None:
        request += "center=%s&" % center
        request += "zoom=%i&" % zoom

    request += "size=%ix%i&" % imgSize
    request += "format=%s&" % imgFormat
    request += "maptype=%s&" % mapType

    # add markers (location and style)
    if markers is not None:
        for marker in markers:
            request += "%s&" % marker

    # request += "mobile=false&" # optional: mobile=true will assume the image is shown on mobile device
    request += "sensor=false&"  # must be given, deals with getting location from mobile device

    return urllib.urlopen(request).read()
    # save image directly to disk
    # urllib.urlretrieve(request, imgDir)
