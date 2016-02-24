

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class AddMangaController(object):
    def __init__(self, library):
        self.library = library
        self.view = AddMangaView(self)

    def close(self):
        self.view.destroy()

    def hide(self):
        self.view.hide()

    def show(self):
        self.view.show()

    def search(self):
        pass

    def add_manga(self):
        pass


class AddMangaView(QWidget):
    def __init__(self, controller):
        super(AddMangaView, self).__init__()
        self.controller = controller

    def setup_ui(self):
        self.action_search = QAction('Search', self)


        self.conbo_box = QComboBox(self)