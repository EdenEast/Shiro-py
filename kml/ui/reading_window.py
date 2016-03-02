from PyQt4.QtGui import *
from PyQt4.QtCore import *

from kml.library import Library
from kml.ui.widgets import kscrollviewer
from PIL import ImageQt, Image
import os
import zipfile


class ReaderWindow(QWidget):

    _ORIGINAL_FIT = 'action_original_fit'
    _VERTICAL_FIT = 'action_vertical_fit'
    _HORIZONTAL_FIT = 'action_horizontal_fit'
    _BEST_FIT = 'action_best_fit'

    def __init__(self, manga, chapter):
        super(ReaderWindow, self).__init__()

        self.label = QLabel()
        self.label.setAlignment(Qt.AlignCenter)
        self.manga = manga
        self.chapter = chapter

        self.global_shortcuts = []
        self.pages = []
        self.current_page = 0
        self.fit_type = ReaderWindow._ORIGINAL_FIT
        self.rotate_angle = 0
        self.color_index = 0

        self.view_container = kscrollviewer.KScrollViewer(self)
        # self.view_container.change_background_color(QColor('#304050')) # Atom blue
        self.view_container.change_background_color(QColor('#262626'))
        self.setBackgroundRole(QPalette.Dark)
        self.view_container.setWidget(self.label)
        self.view_container.setAlignment(Qt.AlignCenter)
        layout = QGridLayout()
        layout.setMargin(0)
        layout.addWidget(self.view_container)
        self.setLayout(layout)
        self.setGeometry(0, 0, 800, 900)
        self._center_window()
        self._define_global_shortcuts()
        self.load_chapter(chapter)
        self.update_page()
        self.show()

    def _define_global_shortcuts(self):
        sequence = {
            'Ctrl+Q': self.close,
            'Ctrl+Shift+Left': self.prev_chapter,
            'Ctrl+Left': self.first_page,
            'Left': self.prev_page,
            'Right': self.next_page,
            'Space': self.next_page,
            'Ctrl+Right': self.last_page,
            'Ctrl+Shift+Right': self.next_chapter,
            'Ctrl+R': self.rotate_right,
            'Ctrl+Shift+R': self.rotate_left,
            'Ctrl+B': self.first_page,
            'Ctrl+E': self.last_page,
            # 'Ctrl+O': controller.open,
            'Ctrl+G': self.change_background_color,
            '1': self.original_fit,
            '2': self.vertical_fit,
            '3': self.horizontal_fit,
            '4': self.best_fit,
        }

        for key, value in sequence.items():
            s = QShortcut(QKeySequence(key), self.view_container, value)
            s.setEnabled(True)
            self.global_shortcuts.append(s)

    def _center_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def closeEvent(self, event):
        # self.deleteLater()
        event.accept()

    def load_chapter(self, chapter):
        file_path = os.path.join(Library.directory, chapter.parent.title, chapter.get_file_name())
        if not os.path.isfile(file_path):
            print('{} does not exist'.format(file_path))
            return
        self.pages.clear()
        with zipfile.ZipFile(file_path) as archive:
            for entry in archive.infolist():
                with archive.open(entry) as file:
                    if '.ini' not in file.name:
                        img = Image.open(file)
                        self.pages.append(img)
        self.current_page = 0

    def set_content(self, content):
        if content:
            self.label.setPixmap(content)
            self.label.resize(content.size())
            self.view_container.reset_scroll_position()
            self.update_title()

    def get_current_page(self):
        if self.current_page < len(self.pages):
            image_qt = ImageQt.ImageQt(self.pages[self.current_page])
            pix_map = QPixmap.fromImage(image_qt.copy())
            pix_map = self._rotate_page(pix_map)
            pix_map = self._resize_page(pix_map)
            return pix_map

    def _rotate_page(self, pix_map):
        if self.rotate_angle != 0:
            transform = QTransform().rotate(self.rotate_angle)
            pix_map = QPixmap(pix_map.transformed(transform))
        return pix_map

    def _resize_page(self, pix_map):
        if self.fit_type == ReaderWindow._VERTICAL_FIT:
            pix_map = pix_map.scaledToHeight(
                self.view_container.size().height() - 2,
                Qt.SmoothTransformation)
        elif self.fit_type == ReaderWindow._HORIZONTAL_FIT:
            pix_map = pix_map.scaledToWidth(
                self.view_container.size().width(),
                Qt.SmoothTransformation)
        elif self.fit_type == ReaderWindow._BEST_FIT:
            ratio = pix_map.width() / pix_map.height()
            if ratio < 1:
                pix_map = pix_map.scaledToWidth(
                    self.view_container.size().width() * 0.8,
                    Qt.SmoothTransformation)
            else:
                pix_map = pix_map.scaledToHeight(
                    self.view_container.size().height() * 0.95,
                    Qt.SmoothTransformation)
        return pix_map

    def update_page(self):
        self.set_content(self.get_current_page())

    def update_title(self):
        title = '{}: {}  ( {} | {} )'.format(self.manga.title, self.chapter.title, self.current_page + 1, len(self.pages))
        self.setWindowTitle(title)

    def on_action_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def next_page(self):
        # Getting the value of the current vertical scroll bar and checking to see
        # if it is at the end/bottom
        value = self.view_container.verticalScrollBar().value()
        maximum = self.view_container.verticalScrollBar().maximum()

        if value == maximum:
            self.goto_next_page()
            return

        # If we are not at the end of the page we need to move down the page
        # Get the page step value from the scroll bar
        page_step = self.view_container.verticalScrollBar().pageStep()
        page_step -= (page_step * 0.15)
        self.view_container.verticalScrollBar().setValue(value + page_step)

    def prev_page(self):
        # Getting the value of the current vertical scroll bar and checking to see
        # if the value is a 0 and we are at the top of the page
        value = self.view_container.verticalScrollBar().value()
        if value == self.view_container.verticalScrollBar().minimum():
            self.goto_prev_page()
            return

        # If we are not at the beginning of the page we need to move the page up
        page_step = self.view_container.verticalScrollBar().pageStep()
        page_step -= (page_step * 0.15)
        self.view_container.verticalScrollBar().setValue(value - page_step)

    def first_page(self):
        self.current_page = 0
        self.update_page()

    def last_page(self):
        self.current_page = len(self.pages) - 1
        self.update_page()

    def goto_next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.update_page()
        else:
            # Setting the chapter that we just read to completed
            Library.db.cursor().execute('UPDATE chapter SET completed=1 WHERE manga_id={} AND title=\'{}\''
                                      .format(self.manga.hash, self.chapter.title))
            Library.db.commit()
            self.next_chapter()

    def goto_prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.update_page()
            self.view_container.verticalScrollBar().setValue(
                    self.view_container.verticalScrollBar().maximum()
                )
        else:
            self.prev_chapter()

    def next_chapter(self):
        chapter = self.manga.next_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.load_chapter(chapter)
            self.update_page()

    def prev_chapter(self):
        chapter = self.manga.prev_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.load_chapter(self.chapter)
            self.current_page = len(self.pages) - 1
            self.update_page()

    def rotate_left(self):
        self.rotate_angle = (self.rotate_angle - 90) % 360
        self.update_page()

    def rotate_right(self):
        self.rotate_angle = (self.rotate_angle + 90) % 360
        self.update_page()

    def original_fit(self):
        self.fit_type = ReaderWindow._ORIGINAL_FIT
        self.update_page()

    def vertical_fit(self):
        self.fit_type = ReaderWindow._VERTICAL_FIT
        self.update_page()

    def horizontal_fit(self):
        self.fit_type = ReaderWindow._HORIZONTAL_FIT
        self.update_page()

    def best_fit(self):
        self.fit_type = ReaderWindow._BEST_FIT
        self.update_page()

    def change_background_color(self):
        if self.color_index == 4:
            self.color_index = 0
        else:
            self.color_index += 1

        if self.color_index == 0:  # Revolution dark grey
            self.view_container.change_background_color(QColor('#262626'))
        elif self.color_index == 1:  # Atom Blue
            self.view_container.change_background_color(QColor('#304050'))
        elif self.color_index == 2:  # mod8 dark blue grey
            self.view_container.change_background_color(QColor('#2B303B'))
        elif self.color_index == 3:
            self.view_container.change_background_color(QColor('#322D29'))
        elif self.color_index == 4:
            self.view_container.change_background_color(QColor('#AE4F4F'))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_F:
            self.on_action_fullscreen()
        if event.key() == Qt.Key_N:
            self.goto_next_page()
        if event.key() == Qt.Key_P:
            self.goto_prev_page()

