from PIL import Image
import cStringIO

cmyk_scale = 100


def load_image(imgDir, width=640, height=480, crop=0):
    """
    loading image to draw

    :param
        imgDir (string) - image file's directory
        width (int)     - image file's width
        height (int)    - image file's height
        crop (int)      - crop the image (remove google logo from satellite image)

    :return
        imageFile - loaded image file
        imgd      - image raw data
    """
    try:
        try:
            imageFile = Image.open(cStringIO.StringIO(imgDir))
        except IOError:
            imageFile = Image.open(imgDir)

        size = width, height

        if crop > 0:
            imageFile = imageFile.crop((0, crop/2, width, height + crop/2))

        imageFile = imageFile.resize(size, Image.ANTIALIAS)

        try:
            imgd = imageFile.tostring("raw", "BGRA")
        except SystemError:
            imageFile.putalpha(256)
            r, g, b, a = imageFile.split()

            imgd = Image.merge("RGBA", (b, g, r, a)).tostring("raw", "RGBA")

        return imageFile, imgd

    except IOError as e:
        print "IOError:", e
        return None, ""
    except Exception as e:
        print e
        return None, ""


def rgb2rgb(rgb):
    """
    normalized rgb color values
    """

    r, g, b, a = rgb

    return r/255.0, g/255.0, b/255.0


def rgb2hsv(rgb):
    """
    converting rgb color values to hsv
    (http://stackoverflow.com/questions/24152553/hsv-to-rgb-and-back-without-floating-point-math-in-python)

    :param
        rgb (float tuple) - red green blue

    :return
        hsv (float tuple) - hue saturation value
    """

    # unpack the tuple for readability
    r, g, b, a = rgb

    # compute the h value by finding the maximum of the rgb values
    rgb_max = max(rgb)
    rgb_min = min(rgb)

    # compute the value
    v = rgb_max
    if v == 0:
        h = s = 0
        return h, s, v

    # compute the saturation value
    s = 255 * (rgb_max - rgb_min) // v

    if s == 0:
        h = 0
        return h, s, v

    # compute the hue
    if rgb_max == r:
        h = 0 + 43 * (g - b) // (rgb_max - rgb_min)
    elif rgb_max == g:
        h = 85 + 43 * (b - r) // (rgb_max - rgb_min)
    else:  # rgb_max == b
        h = 171 + 43 * (r - g) // (rgb_max - rgb_min)

    return h, s, v


def rgb2cmyk(rgb):
    """
    converting rgb color values to cmyk

    :param
        rgb (float tuple) - red green blue

    :return
        cmyk (float tuple) - cyan magenta yellow key
    """

    r, g, b, a = rgb

    if r == 0 and g == 0 and b == 0:
        # black
        return 0, 0, 0, cmyk_scale

    # rgb [0,255] -> cmy [0,1]
    c = 1 - r / 255.0
    m = 1 - g / 255.0
    y = 1 - b / 255.0

    # extract out k [0,1]
    min_cmy = min(c, m, y)
    c = (c - min_cmy) / (1 - min_cmy)
    m = (m - min_cmy) / (1 - min_cmy)
    y = (y - min_cmy) / (1 - min_cmy)
    k = min_cmy

    # rescale to the range [0, cmyk_scale]
    return c * cmyk_scale, m * cmyk_scale, y * cmyk_scale, k * cmyk_scale
