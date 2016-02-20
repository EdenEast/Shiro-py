__author__ = 'Athena'

from kml.models.library import Library
from kml.web.site.mangalife import MangaLife
from kml.ui import library_window
from PyQt4 import QtGui, QtCore
import sys

def main():
    # Creating the library
    library = Library()
    library.load_library()

    app = QtGui.QApplication(sys.argv)
    app.setApplicationName('Kindread Manga Library')
    app.setApplicationVersion('0.0.1')

    # Creating the main window
    main_window = library_window.LibraryWindowController(library)
    main_window.view.setStyle(QtGui.QStyleFactory.create('cleanlook'))
    # main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()