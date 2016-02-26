__author__ = 'Athena'

from kml import library
from kml.web.site import mangalife
from kml.ui import main_window
import sys

from PyQt4.QtGui import QApplication


def main():
    lib = library.Library()
    lib.load()

    # ml = mangalife.MangaLife(lib)
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/Horimiya'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GirlsOfTheWilds'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/GosuTheMaster'))
    # lib.add_manga(ml.create_manga_info_from_url('http://manga.life/read-online/ReLIFE'))

    app = QApplication(sys.argv)
    window = main_window.MainWindow(lib)
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
