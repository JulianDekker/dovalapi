from .IO import IO
from .bokehresources import BokehResources
from .canvasxpressresources import plotcanvas
from .utils import utils


def columnsFromImage():
    img = Image.open(img_file)
    image_name = img.filename

    width, height = img.size
    for i, col in enmumerate(COLUMNS):
        col = COLUMNS.get(str(col))

        cropareas(col, COLUMNS[i+1].get(str(col)), height, width)  # This is where I am stuck

        output_image = img.crop(area)
        output_image.save(image_name)

def cropareas(oldcol, newcol, height, width):
    try:
        area = (oldcol, 0, height, newcol)
    except IndexError:
        area = (oldcol, 0, height, width)
    output_image = img.crop(area)
    output_image.save(image_name)

