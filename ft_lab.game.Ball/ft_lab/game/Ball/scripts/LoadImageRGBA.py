# -----------------------------------------------------.
# Load image (Use PIL).
# -----------------------------------------------------.
import omni.ui
import itertools
from PIL import Image, ImageDraw, ImageFont

class LoadImageRGBA:
    _byte_provider = None
    _width  = 0
    _height = 0

    def __init__(self):
        pass

    def Open (self, path : str):
        try:
            # Load image (RGBA).
            im = Image.open(path).convert('RGBA')

            # Get image size.
            self._width  = im.size[0]
            self._height = im.size[1]

            # Get image data(RGBA buffer).
            imgD = im.getdata()

            # Converting a 2d array to a 1d array.
            byte_data = list(itertools.chain.from_iterable(imgD))

            self._byte_provider = omni.ui.ByteImageProvider()
            self._byte_provider.set_bytes_data(byte_data, [self._width, self._height])

        except Exception as e:
            self._width  = 0
            self._height = 0
            self._byte_provider = None
            print(e)
            return False

        return True
    
    def GetWidth (self):
        return self._width

    def GetHeight (self):
        return self._height

    def GetByteProvider (self):
        return self._byte_provider

