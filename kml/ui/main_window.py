import os
import sys

from PIL import Image, ImageQt
from PyQt4 import QtGui, QtCore, uic

from kml import bg_file_io, bg_downloaded
from kml.library import Library
from kml.ui import reading_window, search_window


class ChapterModel(QtCore.QAbstractTableModel):
    header_data = ['Title', 'Number', 'Completed', 'Downloaded']

    def __init__(self):
        super(ChapterModel, self).__init__()
        self.table = None

    def update(self, data):
        self.emit(QtCore.SIGNAL('layoutAboutToBeChanged()'))
        self.table = data
        self.emit((QtCore.SIGNAL('layoutChanged()')))

    def rowCount(self, index=None, *args, **kwargs):
        if self.table is not None:
            return len(self.table)
        return 0

    def columnCount(self, index=None, *args, **kwargs):
        if self.table is not None:
            return len(self.table[0])
        return 0

    def data(self, index, role=None):
        if role == QtCore.Qt.DisplayRole:
            value = self.table[index.row()][index.column()]
            if value is True or value is False:
                value = 'Yes'if value else ''
            return value
        elif role == QtCore.Qt.BackgroundColorRole:
            row = self.table[index.row()]
            if row[2]:
                return QtGui.QColor('#E1F7D5')
            elif not row[3]:
                return QtGui.QColor('#FFBDBD')
            elif not row[2] and row[3]:
                return QtGui.QColor('#C9C9FF')
        elif role == QtCore.Qt.TextAlignmentRole:
            return QtCore.Qt.AlignCenter
        return None

    def headerData(self, section, orientation, role=None):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self.header_data[section]
            else:
                return ''
        return QtCore.QAbstractTableModel.headerData(self, section, orientation, role)


class Window(QtGui.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        if __name__ == '__main__':
            location = 'main_window.ui'
        else:
            location = 'kml/ui/main_window.ui'
            uic.loadUi(location, self)

        self.download_task = None

        self.icon_size = QtCore.QSize(168, 250)
        self.icon_padding = QtCore.QSize(20, 45)
        self.setWindowIcon(QtGui.QIcon('icon.png'))
        self.setWindowTitle('Kindred Manga Library')

        # Connecting actions
        self.action_update_library.triggered.connect(self.update_library)
        self.action_update_manga.triggered.connect(self.update_manga)
        self.action_single_page_viewer.triggered.connect(self.read_chapter_single_page_viewer)
        self.action_two_page_viewer.triggered.connect(self.read_chapter_two_page_viewer)
        self.action_web_viewer.triggered.connect(self.read_chapter_web_viewer)
        self.action_search_web.triggered.connect(self.search_web)
        self.action_download_chapters.triggered.connect(self.download_manga)
        self.action_set_selected_chapter_read.triggered.connect(self.set_chapter_as_complete)

        # Connecting shortcuts
        sequence = {
            'Escape': self.close,
            'Q': self.close,
            'R': self.read_chapter,
            'Ctrl+R': self.read_next_unread_chapter,
            'U': self.update_manga_list,
            'CTRL+U': self.update_library,
            'D': self.download_manga,
            'Ctrl+D': self.stop_download,
            'Return': self.enter_pressed,
            'Space': self.enter_pressed,
            'Backspace': self.show_manga_list
        }

        for key, value in sequence.items():
            self.connect(QtGui.QShortcut(QtGui.QKeySequence(key), self), QtCore.SIGNAL('activated()'), value)

        # Setting up the manga list
        self.manga_list.setIconSize(self.icon_size)
        self.manga_list.setViewMode(QtGui.QListWidget.IconMode)
        self.manga_list.setMovement(QtGui.QListWidget.Static)
        self.manga_list.setResizeMode(QtGui.QListWidget.Adjust)
        self.manga_list.setWordWrap(True)
        self.manga_list.doubleClicked.connect(self.ml_selected_item)
        self.manga_list.itemSelectionChanged.connect(self.update_info_panel)

        self.chapter_model = ChapterModel()
        self.chapter_table.setModel(self.chapter_model)
        self.chapter_table.horizontalHeader().setResizeMode(QtGui.QHeaderView.Stretch)
        self.chapter_table.setSelectionBehavior(QtGui.QAbstractItemView.SelectRows)
        self.chapter_table.doubleClicked.connect(self.ct_selected_chapter)

        self.btn_back_manga_list.clicked.connect(self.show_manga_list)

        # Settings the stacked widget to the manga list page
        self.stacked.setCurrentIndex(0)
        self.update_manga_list()
        self.manga_list.setCurrentIndex(self.manga_list.model().index(0, 0))
        self.manga_list.setFocus()
        self.resize(1130, 835)
        
    def eventFilter(self, obj, event):
        if event.type() == event.Resize:
            statement = '{} {}'.format(self.width(), self.height())
            print(statement)
        if obj is self.manga_list and event.type() == event.Resize:
            padding = 15 * 2
            div = self.manga_list.width() / (self.icon_size.width() + padding)
            width = self.manga_list.width() / div
            div = self.manga_list.height() / self.icon_size.height()
            height = self.manga_list.height() / div
            grid_size = QtCore.QSize(width, height)
            self.manga_list.setGridSize(grid_size)
        return super(Window, self).eventFilter(obj, event)

    def update_manga_list(self):
        cursor = Library.db.cursor()
        query = "SELECT title, cover_url FROM manga ORDER BY title"
        cursor.execute(query)
        data_query = cursor.fetchall()
        self.manga_list.clear()

        for data in data_query:
            title = data[0]
            cover_file = os.path.join(Library.directory, '.Cover', title + '.jpg')
            if not os.path.isfile(cover_file):
                continue
            # Needs to be a copy as it will resize the actual image in the library dict
            image = Library.covers[title].copy()
            image = image.resize((self.icon_size.width(), self.icon_size.height()), Image.ANTIALIAS)
            pix_map = ImageQt.toqpixmap(image)
            icon = QtGui.QIcon(pix_map)
            item = QtGui.QListWidgetItem(title, self.manga_list)
            item.setStatusTip(title)
            item.setIcon(icon)
            item.setSizeHint(self.icon_size + self.icon_padding)

    def update_info_panel(self):
        cursor = Library.db.cursor()

        # Getting the selected item
        item = self.manga_list.currentItem()

        title = item.text()
        cover = Library.covers[title]
        # cover.thumbnail((235, 350), Image.ANTIALIAS)
        pix_map = ImageQt.toqpixmap(cover)
        pix_map = pix_map.scaledToHeight(350, QtCore.Qt.SmoothTransformation)
        self.cover_label.setPixmap(pix_map)
        self.cover_label.resize(pix_map.size())

        query = "SELECT title, authors, year, genera, publish_status, " \
                "scan_status, description FROM manga WHERE title='{}'".format(title)
        cursor.execute(query)
        data = cursor.fetchone()

        # Breaking up the genre string so that it is not so big
        genre_string = data[3].split(',')
        genre = ''
        character_count = 0
        for g in genre_string:
            word_count = len(g)
            if character_count + word_count >= 24:
                genre += '\n{}'.format(g)
                character_count = word_count
            else:
                if len(genre) == 0:
                    genre = g
                else:
                    genre += ', {}'.format(g)
                character_count += word_count

        title = ''
        character_count = 0
        for word in data[0].split(' '):
            word_count = len(word)
            if character_count + word_count >= 25:
                title += '\n{}'.format(word)
                character_count = word_count
            else:
                if len(title) == 0:
                    title = word
                else:
                    title += ' {}'.format(word)
                    character_count += word_count

        # Setting all of the label to display the information
        self.label_title.setText(title)
        # self.label_title.setText(data[0])
        self.label_author.setText(data[1])
        self.label_year.setText(str(data[2]))
        self.label_genre.setText(genre)
        self.label_publish.setText(data[4])
        self.label_scan.setText(data[5])
        self.description_box.setText(data[6])

    def update_chapter_table(self):
        item = self.manga_list.currentItem()
        title = item.text()

        table = []
        manga = Library.create_manga_from_db_by_title(title)
        for chapter in manga.chapter_list:
            table.append([chapter.title, chapter.number, chapter.completed, chapter.downloaded])
        self.chapter_model.update(table)
        self.chapter_table.selectionModel().clear()

    def show_manga_list(self):
        self.stacked.setCurrentIndex(0)

    def ml_selected_item(self):
        self.stacked.setCurrentIndex(1)
        self.update_chapter_table()
        self.chapter_table.setFocus()

    def ct_selected_chapter(self):
        self.read_chapter()
        pass

    # -----------------------------------------------------------------------------------------
    # Actions

    def read_chapter(self, view_mode=None):
        title = self.manga_list.currentItem().text()
        manga = Library.create_manga_from_db_by_title(title)

        index = self.chapter_table.selectionModel().currentIndex()
        title = self.chapter_model.table[index.row()][0]

        chapter = manga.get_chapter_by_title(title)
        self.reader_view_window = reading_window.ReaderWindow(self, chapter, view_mode)
        self.reader_view_window.show()

    def update_library(self):
        cursor = Library.db.cursor()
        query = 'SELECT title FROM manga'
        query_result = cursor.execute(query).fetchall()

        text = ''
        for title in query_result:
            title = title[0]
            chapters = Library.update_manga_by_title(title)
            text += title + ':\n'
            if len(chapters) > 0:
                for chapter in chapters:
                    text += '     - Title: {} Number: {}\n'.format(chapter.title, chapter.get_number_string())
            else:
                text += '    Up To Date\n'
            text += '\n'

        msg = QtGui.QMessageBox()
        msg.setIcon(QtGui.QMessageBox.Information)
        msg.setText('Updated manga information bellow')
        msg.setDetailedText(text)
        msg.setFixedSize(300, 500)
        msg.setWindowTitle('Updated Library Information')
        msg.exec()

    def update_manga(self):
        title = self.manga_list.currentItem().text()
        self.statusBar().showMessage('Updating {}... '.format(title), 2000)
        chapters = Library.update_manga_by_title(title)
        self.statusBar().showMessage('Updated {} -> [ {} ] new chapter(s).'.format(title, len(chapters)), 5000)
        if len(chapters) > 0:
            text = ''
            for chapter in chapters:
                text += '[Title] - {}\n'.format(chapter.title)
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setDetailedText(text)
            msg.setWindowTitle('{} Updated'.format(title))
            msg.setText('Chapters that were added in update.')
            msg.exec_()
        else:
            msg = QtGui.QMessageBox()
            msg.setIcon(QtGui.QMessageBox.Information)
            msg.setWindowTitle('{} Updated'.format(title))
            msg.setText('{} is up to date'.format(title))
            msg.exec()

    def download_manga(self):
        title = self.manga_list.currentItem().text()
        manga = Library.create_manga_from_db_by_title(title)
        self.download_task = bg_downloaded.ChapterDownloadWorker(self)
        self.download_task.data_downloaded.connect(self.status_message)
        for chapter in manga.chapter_list:
            self.download_task.push(chapter)
        self.download_task.start()

    def stop_download(self):
        self.download_task.abort()

    def read_chapter_single_page_viewer(self):
        self.read_chapter('single')

    def read_chapter_two_page_viewer(self):
        self.read_chapter('double')

    def read_chapter_web_viewer(self):
        self.read_chapter('web')
        pass

    def read_next_unread_chapter(self):
        title = self.manga_list.currentItem().text()
        manga = Library.create_manga_from_db_by_title(title)

        chapter = manga.get_next_chapter_to_read()
        self.reader_view_window = reading_window.ReaderWindow(self, chapter, 'single')
        self.reader_view_window.show()

    def search_web(self):
        self.search_window = search_window.SearchWindow(Library, self)
        self.search_window.show()

    def set_chapter_as_complete(self):
        manga_title = self.manga_list.currentItem().text()
        manga = Library.create_manga_from_db_by_title(manga_title)
        rows = self.chapter_table.selectionModel().selectedRows()
        for index in rows:
            title = self.chapter_model.table[index.row()][0]
            Library.db.cursor().execute("UPDATE chapter SET completed=1 WHERE manga_id={} and title='{}'"
                                        .format(manga.hash, title))
        Library.db.commit()
        self.update_chapter_table()

    def enter_pressed(self):
        if self.stacked.currentIndex() == 0:
            self.ml_selected_item()
        else:
            self.read_chapter()

    def status_message(self, msg):
        self.statusBar().showMessage(msg)

    def closeEvent(self, *args, **kwargs):
        print(self.width(), self.height())
        Library.close()
        bg_file_io.join()


if __name__ == '__main__':

    Library.init_site_list()
    Library.load()
    bg_file_io.initialize()

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())
