from kml.ui import search_window, reading_window
from kml import bg_file_io
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *
from PIL import ImageQt
import os
from kml.library import Library


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()

        # Setting up Qt's database access objects
        self.qdb = QSqlDatabase.addDatabase('QSQLITE')
        self.qdb.setDatabaseName(os.path.join(Library.directory, 'Library.db'))
        self.qdb.open()

        # Creating models for the manga_list_view and chapter_table_view
        self.manga_model = QSqlQueryModel()
        self.manga_model.setQuery('SELECT title FROM manga ORDER BY title')
        self.chapter_model = QSqlQueryModel()

        self.status_bar = self.statusBar()
        self.status_bar.showMessage('testing')

        self.action_exit = QAction('Exit', self)
        self.connect(self.action_exit, SIGNAL('triggered()'), SLOT('close()'))
        self.action_search_new_manga = QAction('Search', self)
        self.action_search_new_manga.triggered.connect(self.search_new_manga_dialog)
        self.action_download_all_chapters = QAction('Download All Chapters', self)
        self.action_download_all_chapters.triggered.connect(self.download_all_chapters)
        self.action_read_chapter = QAction('Read Chapter', self)
        self.action_read_chapter.triggered.connect(self.read_chapter)

        self.file_menu = self.menuBar().addMenu('File')
        self.library_menu = self.menuBar().addMenu('Library')

        self.file_menu.addAction(self.action_exit)
        self.library_menu.addAction(self.action_search_new_manga)
        self.library_menu.addAction(self.action_download_all_chapters)
        self.library_menu.addAction(self.action_read_chapter)

        tool_bar = self.addToolBar('Library')
        tool_bar.addAction(self.action_search_new_manga)

        # Creating Widgets
        self.manga_lv = QListView(self)
        self.manga_lv.setModel(self.manga_model)
        self.manga_lv.selectionModel().selectionChanged.connect(self.on_action_manga_lv)

        self.chapter_tv = QTableView(self)
        self.chapter_tv.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.chapter_tv.verticalHeader().hide()
        header = self.chapter_tv.horizontalHeader()
        header.setResizeMode(QHeaderView.Stretch)

        self.cover_label = QLabel(self)
        self.cover_label.setMinimumSize(150, 300)

        vbox = QVBoxLayout()
        vbox.addWidget(self.manga_lv)
        vbox.addWidget(self.cover_label)
        vbox.setAlignment(self.cover_label, Qt.AlignCenter)
        vbox.setMargin(0)
        vbox_layout = QWidget()
        vbox_layout.setLayout(vbox)

        splitter = QSplitter(Qt.Horizontal)
        splitter.addWidget(vbox_layout)
        splitter.addWidget(self.chapter_tv)
        splitter.setStretchFactor(1, 10)

        self.setCentralWidget(splitter)
        self.setGeometry(0, 0, 1200, 800)
        self._centralize_window()
        self.show()

    def closeEvent(self, event):
        # Checking to see if the user wants to quit
        quit_msg = 'Are you sure you want to Quit?'
        reply = QMessageBox.question(self, 'Close Application', quit_msg, QMessageBox.Yes, QMessageBox.No)
        if reply == QMessageBox.No:
            event.ignore()
            return
        Library.close()
        bg_file_io.join()
        self.qdb.close()
        event.accept()

    def _centralize_window(self):
        frame_geometry = self.frameGeometry()
        monitor_screen_index = QApplication.desktop().screenNumber(QApplication.desktop().cursor().pos())
        center_point = QApplication.desktop().screenGeometry(monitor_screen_index).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def on_action_manga_lv(self, index):
        self.update_chapter_lv()
        # @TODO: update the cover label
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        self.cover_label.setPixmap(QPixmap.fromImage(ImageQt.ImageQt(Library.covers[title]).copy()))

    def update_chapter_lv(self):
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        cursor = Library.db.cursor()
        cursor.execute('SELECT id FROM manga WHERE title=\'{}\''.format(title))
        h = cursor.fetchone()
        cmd = 'SELECT title, number, completed, downloaded FROM chapter WHERE manga_id={} ORDER BY number'.format(h[0])
        self.chapter_model.setQuery(cmd)
        self.chapter_tv.setModel(self.chapter_model)

    def update_manga_lv(self):
        self.manga_model.setQuery('SELECT title FROM manga ORDER BY title')
        self.manga_lv.setModel(self.manga_model)

    def search_new_manga_dialog(self):
        self.window = search_window.SearchWindow(Library, self)
        self.window.show()

    def download_all_chapters(self):
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        cursor = Library.db.cursor()
        cursor.execute('SELECT id FROM manga WHERE title=\'{}\''.format(title))
        hash = cursor.fetchone()
        manga = Library.create_manga_from_db_by_title(title)
        site = Library.site_list[manga.site]
        for chapter in manga.chapter_list:
            self.statusBar().showMessage('Downloading {}: {}'.format(manga.title, chapter.title))
            site.download_chapter_threaded(chapter)
            cmd = 'UPDATE chapter SET downloaded=1 WHERE manga_id={} AND title=\'{}\''.format(hash[0], chapter.title)
            cursor.execute(cmd)
            Library.db.commit()
        self.statusBar().showMessage('Downloading {} Complete.'.format(manga.title), 2000)

    def read_chapter(self):
        # Getting the current manga
        index = self.manga_lv.selectionModel().currentIndex()
        title = self.manga_lv.model().itemData(index)[0]
        manga = Library.create_manga_from_db_by_title(title)

        index = self.chapter_tv.selectionModel().currentIndex()
        title = self.chapter_tv.model().data(index)

        chapter = manga.get_chapter_by_title(title)
        self.reader_view_window = reading_window.ReaderWindow(manga, chapter)

