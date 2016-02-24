__author__ = 'Athena'

from PyQt4.QtGui import *
from kml.ui import download_window


class SearchWindowController(object):
    def __init__(self, library):
        self.library = library
        self.view = SearchWindowView(self)


    def close(self):
        self.view.destroy()

    def hide(self):
        self.view.hide()

    def show(self):
        self.view.show()

    def search(self):
        search_term = self.view.search_term.text()
        manga_site = self.view.combo_box.currentText()
        manga_site = self.library.site_list[manga_site]
        self.result_list = manga_site.get_list_search_results(search_term)
        self.view.list.clear()
        for result in self.result_list:
            self.view.list.addItem(result[0])

    def download_manga(self):
        text = self.view.list.currentItem().text()
        for result in self.result_list:
            if result[0] == text:
                site = self.library.site_list[result[2].get_name()]
                manga = site.create_manga_from_url(result[1])
                manga_download_window = download_window.DownloadWindowController(self.library, manga)
                manga_download_window.show()
                self.hide()


class SearchWindowView(QWidget):
    def __init__(self, controller):
        super(SearchWindowView, self).__init__()
        self.controller = controller
        self.setup_ui()

    def setup_ui(self):
        self.action_search = QAction('Search', self)

        self.combo_box = QComboBox(self)
        self.search_term = QLineEdit(self)
        self.search_term.returnPressed.connect(self.controller.search)
        self.list = QListWidget(self)
        self.download_button = QPushButton('Download Manga', self)
        self.download_button.clicked.connect(self.controller.download_manga)
        hbox = QHBoxLayout()
        hbox.setMargin(0)
        hbox.addWidget(self.search_term)
        hbox.addWidget(self.combo_box)
        hbox_widget = QWidget(self)
        hbox_widget.setLayout(hbox)
        vbox = QVBoxLayout()
        vbox.addWidget(hbox_widget)
        vbox.addWidget(self.list)
        vbox.addWidget(self.download_button)
        self.setLayout(vbox)

        for key in self.controller.library.site_list.keys():
            self.combo_box.addItem(self.controller.library.site_list[key].get_name())

        self.setGeometry(0, 0, 600, 350)
        self._centralize_window()

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
