__author__ = 'Athena'

from PyQt4 import QtGui, QtCore
from PIL.Image import Image
from PIL.ImageQt import ImageQt

class Page(object):
    pass

def pil_to_qpixmap(image):
    im = ImageQt(image)
    return QtGui.QPixmap.fromImage(im.copy())

# loads an image and returns a QPixelMap object
def load_image_qpm(filepath):
    image = Image(filepath)
    pix_map = pil_to_qpixmap(image)
    return pix_map

class Viewer(QtGui.QWidget):
    pass
