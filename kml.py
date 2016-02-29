__author__ = 'Athena'

from kml.library import Library
from kml.web.site import mangalife
from kml.ui import main_window, reading_window
import sys

from PyQt4.QtGui import QApplication


def main():
    Library.init_site_list()
    Library.load()

    # ml = mangalife.MangaLife(lib)
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/Horimiya'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GirlsOfTheWilds'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GosuTheMaster'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/ReLIFE'))

    manga = Library.create_manga_from_db_by_title('Gosu (The Master)')

    app = QApplication(sys.argv)
    window = main_window.MainWindow()
    # window = reading_window.ReaderWindow(manga, manga.chapter_list[0])
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
