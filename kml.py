__author__ = 'Athena'

# from kml.gui import main as run
# run()

import sys

from PyQt4 import QtGui

from kml.ui.manga_reader_controller import MainWindowController


def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Kindred Manga Library")
    app.setApplicationVersion('1.0.0')

    main_window = MainWindowController()
    # main_window.open()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

