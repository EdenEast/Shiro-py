from PyQt4.QtGui import *
from kml.lib import Library


class SearchWindow(QWidget):
    def __init__(self, library, parent):
        super(SearchWindow, self).__init__()
        self.parent = parent
        self.result_list = []

        # Create widgets
        self.combo_box = QComboBox(self)
        self.search_term = QLineEdit(self)
        self.search_term.returnPressed.connect(self.search)
        self.search_term.setFocus()
        self.list = QListWidget(self)
        self.add_button = QPushButton('Add Manga', self)
        self.add_button.clicked.connect(self.add_manga)

        hbox = QHBoxLayout()
        hbox.setMargin(0)
        hbox.addWidget(self.search_term)
        hbox.addWidget(self.combo_box)

        vbox = QVBoxLayout()
        vbox.addLayout(hbox)
        vbox.addWidget(self.list)
        vbox.addWidget(self.add_button)
        self.setLayout(vbox)

        self.setWindowIcon(QIcon('icon.ico'))
        for key in Library.site_list.keys():
            self.combo_box.addItem(Library.site_list[key].get_name())

        self.setGeometry(0, 0, 600, 350)
        self._centralize_window()

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def search(self):
        term = self.search_term.text()
        site_text = self.combo_box.currentText()
        site = Library.site_list[site_text]
        self.result_list = site.get_list_search_results(term)
        self.list.clear()
        for result in self.result_list:
            self.list.addItem(result[0])

    def add_manga(self):
        if self.list.currentItem() is None:
            return
        text = self.list.currentItem().text()
        for result in self.result_list:
            if result[0] == text:
                site = Library.site_list[result[2].get_name()]
                manga = site.create_manga_info_from_url(result[1])
                Library.add_manga(manga)
                self.parent.update_manga_list()
                self.close()
