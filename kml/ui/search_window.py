__author__ = 'Athena'

from PyQt4.QtGui import *

class SearchWindowController(object):
    def __init__(self, library):
        self.library = library
        self.view = SearchWindowView(self)


    def close(self):
        pass

    def show(self):
        self.view.show()


class SearchWindowView(QWidget):
    def __init__(self, controller):
        super(SearchWindowView, self).__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.combo_box = QComboBox(self)
        vbox = QVBoxLayout()
        vbox.addWidget(self.combo_box)
        self.setLayout(vbox)

        for key in self.controller.library.site_list.keys():
            self.combo_box.addItem(self.controller.library.site_list[key].get_name())
