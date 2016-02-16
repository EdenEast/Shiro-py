__author__ = 'Athena'

import zipfile

from PyQt4 import QtGui, QtCore
from PIL import Image
from PIL.ImageQt import ImageQt

from kml.path_file_filter import PathFileFilter
from kml.models.chapter import Chapter
from kml.models.manga import Manga


class MainWindowModel(object):
    _ORIGINAL_FIT = 'action_original_fit'
    _VERTICAL_FIT = 'action_vertical_fit'
    _HORIZONTAL_FIT = 'action_horizontal_fit'
    _BEST_FIT = 'action_best_fit'

    def __init__(self, controller):
        self.controller = controller
        self.chapter = None
        self.fit_type = MainWindowModel._ORIGINAL_FIT
        self.rotate_angle = 0
        self.current_directory = ''
        self.ext_list = ['*.cbr', '*.cbz', '*.zip', '*.rar']
        self.path_file_filter = PathFileFilter(self.ext_list)

        self.page_list = []
        self.current_page = 0

    def open(self, file_name, initial_page=0):
        # Opening the zip file and reading all of the images in it and storing them in a image_list
        # The images are Pillow images and not QT images because they are much better lets be real
        # http://stackoverflow.com/questions/33166316/how-to-read-an-image-inside-a-zip-file-with-pil-pillow
        # image_list = []
        # with zipfile.ZipFile(file_name) as archive:
        #     for entry in archive.infolist():
        #         with archive.open(entry) as file:
        #             img = Image.open(file)
        #             image_list.append(img)
        #
        # self.page_list = image_list
        # self.current_page = 0

        self.chapter = Chapter(Manga('Horimiya', 'MangaLife', 'http://manga.life/read-online/Horimiya'), 'Horimiya', 'url', 37, 0, )
        with zipfile.ZipFile(file_name) as archive:
            for entry in archive.infolist():
                with archive.open(entry) as file:
                    img = Image.open(file)
                    self.chapter.pages.append(img)
        self.page_list = self.chapter.pages
        self.current_page = 0

    def get_current_page(self):
        if self.current_page < len(self.page_list):
            iamge_qt = ImageQt(self.page_list[self.current_page])
            pix_map = QtGui.QPixmap.fromImage(iamge_qt.copy())
            pix_map = self._rotate_page(pix_map)
            pix_map = self._resize_page(pix_map)
            return pix_map

    def _rotate_page(self, pix_map):
        if self.rotate_angle != 0:
            trans = QtGui.QTransform().rotate(self.rotate_angle)
            pix_map = QtGui.QPixmap(pix_map.transformed(trans))
        return pix_map

    def _resize_page(self, pix_map):
        if self.fit_type == MainWindowModel._VERTICAL_FIT:
            pix_map = pix_map.scaledToHeight(
                self.controller.get_current_view_container_size().height() - 2,
                QtCore.Qt.SmoothTransformation)

        elif self.fit_type == MainWindowModel._HORIZONTAL_FIT:
            pix_map = pix_map.scaledToWidth(
                self.controller.get_current_view_container_size().width(),
                QtCore.Qt.SmoothTransformation)
        elif self.fit_type == MainWindowModel._BEST_FIT:
            ratio = pix_map.width() / pix_map.height()
            if ratio < 1:
                pix_map = pix_map.scaledToWidth(
                    self.controller.get_current_view_container_size().width() * 0.8,
                    QtCore.Qt.SmoothTransformation)
            else:
                pix_map = pix_map.scaledToHeight(
                    self.controller.get_current_view_container_size().height() * 0.95,
                    QtCore.Qt.SmoothTransformation)
        return pix_map

    def rotate_left(self):
        self.rotate_angle = (self.rotate_angle - 90) % 360
        self.controller.set_view_content(self.get_current_page())

    def rotate_right(self):
        self.rotate_angle = (self.rotate_angle + 90) % 360
        self.controller.set_view_content(self.get_current_page())

    # ----------------------------------------------------------------------------------
    # Moving pages and chapters
    def next_page(self):
        if self.current_page <= len(self.page_list) - 1:
            self.current_page += 1
            self.controller.set_view_content(self.get_current_page())
            return True
        return False

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.controller.set_view_content(self.get_current_page())
            return True
        return False

    # ----------------------------------------------------------------------------------
    # Page Views
    def original_fit(self):
        self.fit_type = MainWindowModel._ORIGINAL_FIT
        self.controller.set_view_content(self.get_current_page())

    def vertical_fit(self):
        self.fit_type = MainWindowModel._VERTICAL_FIT
        self.controller.set_view_content(self.get_current_page())

    def horizontal_fit(self):
        self.fit_type = MainWindowModel._HORIZONTAL_FIT
        self.controller.set_view_content(self.get_current_page())

    def best_fit(self):
        self.fit_type = MainWindowModel._BEST_FIT
        self.controller.set_view_content(self.get_current_page())





# Saving this for future use
# def pil_to_pixmap(im):
#    # Thank you skilldrick for the for python 3 and on windows.... uhhhhhh :/
#    # http://skilldrick.co.uk/2010/03/pyqt-pil-and-windows/
#    image = ImageQt.ImageQt(im)
#    return QtGui.QPixmap.fromImage(image.copy())
