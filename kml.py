__author__ = 'Athena'

# from kml.gui import main as run
# run()


from kml.ui.manga_reader_controller import MainWindowController
from PyQt4 import QtGui, QtCore
from kml.web.site.mangalife import MangaLife
from kml.ui.library_window_view import LibraryWindowView
from kml.models.library import Library
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

def testing():
    library = Library()
    library.load_library()

    # ml = MangaLife()
    # manga = ml.create_manga_from_url('http://manga.life/read-online/BlackGod')
    # library.add_manga(manga)
    # library.save_library()

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Kindread Manga Library')
    app.setApplicationVersion('0.0.1')
    app.setStyle(QtGui.QStyleFactory.create('cleanlook'))

    main_window = LibraryWindowView(library)
    main_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    # main()
    testing()
