__author__ = 'Athena'

from kml.library import Library
from kml.ui import main_window
from kml import bg_file_io
from PyQt4 import QtGui
import sys

def main():
    Library.init_site_list()
    Library.load()
    bg_file_io.initialize()

    app = QtGui.QApplication(sys.argv)
    window = main_window.Window()
    window.show()
    sys.exit(app.exec_())
    pass

if __name__ == '__main__':
    main()

"""
Something similar to what i am trying to do on osx https://github.com/DrabWeb/Komikan
MyAnimeList package documentation http://python-mal.readthedocs.org/en/latest/getting_started.html
"""
