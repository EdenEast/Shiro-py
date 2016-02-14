__author__ = 'Athena'


from PyQt4 import QtGui
from kml.web.baseparser import BaseParser


class Page(object):
    def __init__(self, data, title, number):
        self._pixmap = False
        self.data = data
        self.title = title
        self.number = number

    @property
    def pixmap(self):
        if not self._pixmap:
            self._pixmap = QtGui.QPixmap()
            self._pixmap.loadFromData(self.data)
        return self._pixmap


class OnlinePage(object):
    def __init__(self, url, title, number, parser):
        if not isinstance(parser, BaseParser):
            raise TypeError
        self.url = url
        self.title = title
        self.number = number
        self.parser = parser
        self._image_url = False

    @property
    def image_url(self):
        if not self._image_url:
            try:
                self.parser.update_image_url(self.url)[0]
            except IndexError as excp:
                print ('[Error]: image_url is empty' + excp.message)
                self._image_url = False
        return self._image_url

    @image_url.setter
    def image_url(self, value):
        self.url = value
        self._image_url = False