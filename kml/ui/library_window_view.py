__author__ = 'Athena'

from PyQt4.QtGui import *
from PyQt4.QtCore import *

from kml.models.data_model import ChapterTableViewModel


class LibraryWindowView(QMainWindow):
    def __init__(self, library):
        super(LibraryWindowView, self).__init__()

        # Saving a reference to the library object
        self.library = library

        # Settings up the ui here
        self.setup_ui()

        self.setWindowIcon(QIcon('icon.png'))

        # Setting up the window size and position on the screen
        self.reset_window_default_size()
        self._centralize_window()

        self.update_manga_list_view()


    def setup_ui(self):
        # Making sure that the window has a status bar
        self.statusBar()

        # Create Actions
        self.action_exit = QAction('Exit', self)

        # Create menu and menu items
        self.file_menu = self.menuBar().addMenu('&File')
        self.file_menu.addAction(self.action_exit)

        # @TODO: Create Toolbars

        # Create Widgets and Layouts
        self.splitter = QSplitter(Qt.Horizontal)

        self.manga_list_view = QListView(self)
        self.chapter_table_view = QTableView(self)
        self.manga_list_view.setModel(self.library.manga_list_model)

        self.chapter_table_view_model = ChapterTableViewModel()
        self.chapter_table_view.setModel(self.chapter_table_view_model)

        self.manga_list_view.clicked.connect(self.on_action_manga_list_view_clicked)
        self.manga_list_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chapter_table_view.setSelectionMode(QAbstractItemView.SingleSelection)
        self.chapter_table_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        header = self.chapter_table_view.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

        self.splitter.addWidget(self.manga_list_view)
        self.splitter.addWidget(self.chapter_table_view)
        self.splitter.setStretchFactor(1, 10)

        hbox = QHBoxLayout()
        hbox.addWidget(self.splitter)

        # @HACK Creating a 'layout_widget' as I cant add a layout as the centeral widget for a QMainWindow
        layout_widget = QWidget(self)
        layout_widget.setLayout(hbox)
        self.setCentralWidget(layout_widget)


    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def reset_window_default_size(self):
        # self.setSizePolicy(QSizePolicy.set)
        self.setMinimumSize(1200, 800)

    def update_manga_list_view(self):
        # model = QStandardItemModel(self.manga_list_view)
        # for manga in self.library.manga_list:
        #     item = QStandardItem(manga.title)
        #     model.appendRow(item)
        # self.manga_list_view.setModel(model)
        pass

    def update_chapter_table_view(self):
        # selectionModel reference http://pyqt.sourceforge.net/Docs/PyQt4/qitemselectionmodel.html
        # manga_index = self.manga_list_view.selectionModel().currentIndex()
        # selected_manga = self.library.get_manga_by_title(self.manga_list_view.model().itemData(manga_index)[0])
        # model = QStandardItemModel(self.chapter_list_view)
        # for chapter in selected_manga.chapter_list:
        #     item = QStandardItem(chapter.title)
        #     model.appendRow(item)
        # self.chapter_list_view.setModel(model)

        manga_index = self.manga_list_view.selectionModel().currentIndex()
        selected_manga = self.library.get_manga_by_title(self.manga_list_view.model().itemData(manga_index)[0])
        new_data = []

        for chapter in selected_manga.chapter_list:
            value = [chapter.get_number_string(), chapter.title, chapter.is_complete, chapter.is_downloaded]
            new_data.append(value)
        self.chapter_table_view_model._data = new_data
        self.chapter_table_view.model().layoutChanged.emit()

    def on_action_manga_list_view_clicked(self, index):
        self.update_chapter_table_view()
