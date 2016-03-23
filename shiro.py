from shiro.library import Library
from shiro.ui import main_window
from shiro import bg_file_io
from PyQt4 import QtGui
import sys
import os


def main():
    app = QtGui.QApplication(sys.argv)
    settings_file = Library.get_settings_file_name()
    if not os.path.isfile(settings_file):
        # settings_window = settings_popup.SettingsPopup()
        # t = ThreadedWindow(settings_window)
        # t.start()
        # t.join()
        folder = str(QtGui.QFileDialog.getExistingDirectory(None, "Select Library Directory"))
        if not folder:
            exit()
        with open(settings_file, 'w') as file:
            file.write('[Library]\nlibrary_directory={}'.format(folder))

    Library.init_site_list()
    Library.load()
    bg_file_io.initialize()

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
