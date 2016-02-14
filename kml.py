__author__ = 'Athena'

# from kml.gui import main as run
# run()

from kml.main_window_controller import MainWindowController
from PyQt4 import QtGui, QtCore
import sys

def main():
    app = QtGui.QApplication(sys.argv)
    app.setApplicationName("Kindred Manga Library")
    app.setApplicationVersion('1.0.0')

    main_window = MainWindowController()
    main_window.open()
    main_window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()

