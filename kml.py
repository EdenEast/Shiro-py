__author__ = 'Athena'

from kml import bg_file_io
from kml.library import Library
from kml.web.site import mangalife
from kml.ui import main_window, reading_window, window_main
import sys

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from kml.ui.widgets import kviewers

def main():
    bg_file_io.initialize()
    Library.init_site_list()
    Library.load()

    # ml = mangalife.MangaLife(lib)
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/Horimiya'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GirlsOfTheWilds'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GosuTheMaster'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/ReLIFE'))

    # manga = Library.create_manga_from_db_by_title('Gosu (The Master)')

    app = QApplication(sys.argv)
    window = main_window.MainWindow()
    # window = reading_window.ReaderWindow(manga, manga.chapter_list[0])
    sys.exit(app.exec())


class Window(QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.view_content = kviewers.KWebViewer()
        self.global_shortcuts = []
        self.define_global_shortcuts()
        self.current_page = 0
        self.setCentralWidget(self.view_content)

        self.manga = Library.create_manga_from_db_by_title('Horimiya')
        self.chapter = self.manga.chapter_list[0]
        self.view_content.set_chapter(self.chapter)
        ml = mangalife.MangaLife(Library)
        link_list = ml.get_all_pages_from_chapter(self.chapter.url)
        for link in link_list:
            self.view_content.add_image_url(link)
        self.view_content.reload_chapter()

    def define_global_shortcuts(self):
        sequence = {
            'Ctrl+Shift+Left': self.prev_chapter,
            'Ctrl+Left': self.first_page,
            'Left': self.prev_page,
            'Right': self.next_page,
            'Space': self.next_page,
            'Ctrl+Right': self.last_page,
            'Ctrl+Shift+Right': self.next_chapter,
            'Ctrl+B': self.first_page,
            'Ctrl+E': self.last_page,
        }

        for key, value in sequence.items():
            s = QShortcut(QKeySequence(key), self.view_content, value)
            s.setEnabled(True)
            self.global_shortcuts.append(s)

    def next_page(self):
        self.view_content.next_page()

    def prev_page(self):
        self.view_content.prev_chapter()

    def first_page(self):
        self.view_content.first_page()

    def last_page(self):
        self.view_content.last_page()

    def prev_chapter(self):
        self.view_content.prev_chapter()

    def next_chapter(self):
        self.view_content.next_chapter()


def testing():
    bg_file_io.initialize()
    Library.init_site_list()
    Library.load()

    app = QApplication(sys.argv)
    window = window_main.MainWindowRedesign()
    window.show()
    sys.exit(app.exec())


def develop():
    Library.init_site_list()
    Library.load()

    ml = mangalife.MangaLife(Library)
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/AkaAkatoretachiNoMonogatari'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GosuTheMaster'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/HakoiriDrops'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/Horimiya'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/PandoraHearts'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/ReLIFE'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/TaiyouNoIe'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/TheBreaker'))
    Library.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/TheBreakerNewWaves'))

if __name__ == '__main__':
    # main()
    # develop()
    testing()

"""
Something similar to what i am trying to do on osx https://github.com/DrabWeb/Komikan
MyAnimeList package documentation http://python-mal.readthedocs.org/en/latest/getting_started.html
"""
