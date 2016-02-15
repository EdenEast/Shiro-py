__author__ = 'Athena'

# from kml.gui import main as run
# run()


from kml.ui.manga_reader_controller import MainWindowController
from PyQt4 import QtGui
from kml.web.site.mangalife import MangaLife
import sys


def main():
    # Testing Scraping MangaLife site
    # ml = MangaLife()
    # manga = ml.create_manga_from_url('http://manga.life/read-online/Horimiya')
    # ml.download_chapter(manga.chapter_list[36])

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Kindred Manga Library")
    app.setApplicationVersion('1.0.0')

    main_window = MainWindowController()
    # main_window.open()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

