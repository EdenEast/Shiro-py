__author__ = 'Athena'

from PyQt4.QtGui import *
from PyQt4.QtCore import Qt


class DownloadWindowController(object):
    def __init__(self, library, manga):
        self.library = library
        self.manga = manga
        self.view = DownloadWindowView(self)

        for chapter in self.manga.chapter_list:
            item = QListWidgetItem(chapter.title)
            # item.setFlags(item.flags() | Qt.Unchecked)
            # item.setCheckState(Qt.Unchecked)
            self.view.chapter_list.addItem(item)

    def show(self):
        self.view.show()

    def deselect(self):
        self.view.chapter_list.clearSelection()

    def download_chapters(self):
        # TODO: List of chapters that have have to download
        selected_chapters = self.view.chapter_list.selectedItems()
        self.library.add_manga(self.manga)
        for selected in selected_chapters:
            chapter = self.manga.get_chapter_by_title(selected.text())
            self.library.site_list[self.manga.manga_site].download_chapter(chapter, self.library.libray_directory)
            print('Downloading {}: Chapter {}'.format(chapter.parent.title, chapter.title))
            self.library.get_manga_by_title(self.manga.title).get_chapter_by_title(chapter.title).downloaded = True
        self.view.hide()


class DownloadWindowView(QWidget):
    def __init__(self, controller):
        super(DownloadWindowView, self).__init__()
        self.controller = controller
        self.chapter_list = QListWidget(self)
        self.chapter_list.setSelectionMode(QListWidget.MultiSelection)
        self.deselect_button = QPushButton('Deselect', self)
        self.deselect_button.pressed.connect(self.controller.deselect)
        self.download_button = QPushButton('Download', self)
        self.download_button.pressed.connect(self.controller.download_chapters)
        vbox = QVBoxLayout()
        vbox.addWidget(self.chapter_list)
        vbox.addWidget(self.deselect_button)
        vbox.addWidget(self.download_button)
        self.setLayout(vbox)
        self.setGeometry(0, 0, 600, 450)
        self._centralize_window()

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())


