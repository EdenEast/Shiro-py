__author__ = 'Athena'

from PyQt4.QtGui import *
from PyQt4.QtCore import *
from kml.models.gui_data_models import MangaListViewModel, ChapterListViewModel
from kml.ui import search_window, download_window
from PIL.ImageQt import ImageQt


# ----------------------------------------------------------------------------------------------------------------------
# Controller
class LibraryWindowController(object):
    def __init__(self, library):
        self.library = library
        self.view = LibraryWindowView(self)
        self.view.show()

    def close(self):
        # Checking to make sure that you want to close the application
        quit_msg = "Are you sure you want to exit the program?"
        reply = QMessageBox.question(self.view, 'Message', quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.Yes:
            # Save the library file
            print('Saving the library file')
            self.library.save_library()
            QCoreApplication.instance().quit()

    def search_online(self):
        search_controller = search_window.SearchWindowController(self.library)
        search_controller.show()

    def download_chapters_from_selected_manga(self):
        index = self.view.manga_list_view.selectionModel().currentIndex()
        selected_manga = self.library.get_manga_by_title(self.view.manga_list_view.model().itemData(index)[0])
        controller = download_window.DownloadWindowController(self.library, selected_manga)
        controller.show()


# ----------------------------------------------------------------------------------------------------------------------
# View
class LibraryWindowView(QMainWindow):
    _DEFAULT_WIDTH = 1200
    _DEFAULT_HEIGHT = 800

    def __init__(self, controller):
        self.controller = controller
        self.selected_manga = None

        self.setup_ui()
        self.set_minimum_default_size()
        self._centralize_window()

    def setup_ui(self):
        super(LibraryWindowView, self).__init__()
        # Making sure that the window has a status bar
        self.statusBar()

        # Create Actions
        self.action_exit = QAction('Exit', self)
        self.action_exit.setShortcut('Ctrl+Q')
        self.action_exit.setStatusTip('Exit Application')
        self.action_exit.triggered.connect(self.controller.close)

        self.action_read_chapter = QAction('Read Chapter', self)
        self.action_read_chapter.setShortcut('Ctrl+R')
        self.action_read_chapter.setStatusTip('Read Chapter')

        self.action_check_for_updates = QAction('Check for Updates', self)
        self.action_check_for_updates.setShortcut('Ctrl+U')
        self.action_check_for_updates.setStatusTip('Check the web for updates for your library')

        self.action_search_online = QAction('Search online', self)
        self.action_search_online.setShortcut('Ctrl+S')
        self.action_search_online.setStatusTip('Search for manga online')
        self.action_search_online.triggered.connect(self.controller.search_online)

        self.action_download_chapter_from_manga = QAction('Download Chapters', self)
        self.action_download_chapter_from_manga.setStatusTip('Show download chapter window for selected manga')
        self.action_download_chapter_from_manga.triggered.connect(self.controller.download_chapters_from_selected_manga)

        # Creating menu bar
        file_menu = self.menuBar().addMenu('File')
        file_menu.addAction(self.action_exit)

        library__menu = self.menuBar().addMenu('Library')
        library__menu.addAction(self.action_read_chapter)
        library__menu.addAction(self.action_search_online)
        library__menu.addAction(self.action_check_for_updates)
        # library__menu.addAction(self.action_download_chapter_from_manga)

        tool_bar = self.addToolBar('Library')
        tool_bar.addAction(self.action_read_chapter)
        tool_bar.addAction(self.action_search_online)
        tool_bar.addAction(self.action_check_for_updates)
        tool_bar.addAction(self.action_download_chapter_from_manga)

        # Create Widgets
        self.splitter = QSplitter(Qt.Horizontal)

        self.manga_list_view = QListView(self)
        self.manga_list_view.setModel(self.controller.library.manga_model)
        self.manga_list_view.selectionModel().selectionChanged.connect(self.on_action_manga_list_view)

        self.chapter_table_view = QTableView(self)
        self.chapter_table_view_model = ChapterListViewModel()
        self.chapter_table_view.setModel(self.chapter_table_view_model)
        self.chapter_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chapter_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self.chapter_table_view.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

        self.cover_label = QLabel(self)
        self.cover_label.setMinimumSize(150, 300)
        vbox = QVBoxLayout()
        vbox.addWidget(self.manga_list_view)
        vbox.addWidget(self.cover_label)
        vbox.setAlignment(self.cover_label, Qt.AlignCenter)
        vbox.setMargin(0)
        vbox_widget = QWidget(self)
        vbox_widget.setLayout(vbox)

        self.splitter.addWidget(vbox_widget)
        self.splitter.addWidget(self.chapter_table_view)
        self.splitter.setStretchFactor(1, 10)

        hbox = QHBoxLayout()
        hbox.addWidget(self.splitter)

        # @HACK Creating a 'layout_widget' as I cannot add a layout as the central widget for a QMainWindiw
        layout_widget = QWidget(self)
        layout_widget.setLayout(hbox)
        self.setCentralWidget(layout_widget)

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def set_minimum_default_size(self):
        self.setMinimumSize(LibraryWindowView._DEFAULT_WIDTH, LibraryWindowView._DEFAULT_HEIGHT)

    def update_chapter_table_view(self):
        manga_index = self.manga_list_view.selectionModel().currentIndex()
        selected_manga = self.controller.library.get_manga_by_title(
            self.manga_list_view.model().itemData(manga_index)[0])
        self.selected_manga = selected_manga
        self.chapter_table_view_model.set_data(selected_manga.chapter_list)

    def on_action_manga_list_view(self, index):
        self.update_chapter_table_view()
        # Changing the cover photo of the cover label
        if self.selected_manga.title in self.controller.library.covers:
            cover_image = self.controller.library.covers[self.selected_manga.title]
            self.cover_label.setPixmap(QPixmap.fromImage(ImageQt(cover_image).copy()))


# ----------------------------------------------------------------------------------------------------------------------
# Model
class LibraryWindowModel(object):
    def __init__(self):
        pass