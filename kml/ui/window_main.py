

from kml import bg_file_io, bg_downloaded
from kml.library import Library
from kml.web import web_utility
from kml.ui import search_window, reading_window
from PyQt4.QtGui import *
from PyQt4.QtCore import *
from PyQt4.QtSql import *

from PIL import Image, ImageQt, ImageDraw
import os


class ChapterModel(QAbstractTableModel):
    header_data = ['Title', 'Number', 'Completed', 'Downloaded']

    def __init__(self, parent=None, *args):
        super(ChapterModel, self).__init__()
        self.table = None

    def update(self, data):
        self.emit(SIGNAL('layoutAboutToBeChanged()'))
        self.table = data
        self.emit(SIGNAL('layoutChanged()'))

    def rowCount(self, index=None, *args, **kwargs):
        if self.table is not None:
            return len(self.table)
        return 0

    def columnCount(self, index=None, *args, **kwargs):
        if self.table is not None:
            return len(self.table[0])
        return 0

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            row = self.table[index.row()]
            value = row[index.column()]
            if value is True or value is False:
                value = "Yes" if value else ""
            return value
        elif role == Qt.BackgroundColorRole:
            row = self.table[index.row()]
            if row[2] is True:
                return QColor('#E1F7D5')
            elif row[3] is False:
                return QColor('#FFBDBD')
            elif row[2] == False and row[3] == True:
                return QColor('#C9C9FF')
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        # elif role == Qt.CheckStateRole:
        #     if index.column() == 0 or index.column() == 1:
        #         return
        #     value = self.table[index.row()][index.column()]
        #     if value:
        #         return Qt.Checked
        #     else:
        #         return Qt.Unchecked
        return None

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_data[section]
            else:
                return ''
        return QAbstractTableModel.headerData(self, section, orientation, role)


def round_corners(img, rad):
    circle = Image.new('L', (rad * 2, rad * 2), 0)
    draw = ImageDraw.Draw(circle)
    draw.ellipse((0, 0, rad * 2, rad * 2), fill=255)
    alpha = Image.new('L', img.size, 255)
    w, h = img.size
    alpha.paste(circle.crop((0, 0, rad, rad)), (0, 0))
    alpha.paste(circle.crop((0, rad, rad, rad * 2)), (0, h - rad))
    alpha.paste(circle.crop((rad, 0, rad * 2, rad)), (w - rad, 0))
    alpha.paste(circle.crop((rad, rad, rad * 2, rad * 2)), (w - rad, h - rad))
    img.putalpha(alpha)
    return img


# def remove_widgets(layout):
#     if layout is not None:
#         while layout.count():
#             child = layout.takeAt(0)
#             if child.widget() is not None:
#                 child.widget().deleteLater()
#                 layout.removeWidget(child.widget())
#             elif child.layout() is not None:
#                 remove_widgets(child.layout())

def clear_layout(layout):
    for i in reversed(range(layout.count())):
        item = layout.itemAt(i)

        if isinstance(item, QWidgetItem):
            print('widget ' + str(item))
            item.widget().close()
        elif isinstance(item, QSpacerItem):
            print('spacer ' + str(item))
        else:
            print('layout ' + str(item))
            clear_layout(item.layout())
        layout.removeItem(item)


class MainWindowRedesign(QMainWindow):
    def __init__(self):
        super(MainWindowRedesign, self).__init__()

        self.global_shortcuts = []

        self.icon_size = QSize(100, 200)
        # self.setCentralWidget(self.manga_list_widget)

        self.splitter = QSplitter(Qt.Horizontal)

        # Creating the manga info section
        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignCenter)
        self.cover_label = QLabel()

        title_label = QLabel('Title: ')
        self.label_title = QLabel()
        hbox1 = QHBoxLayout()
        hbox1.addWidget(title_label)
        hbox1.addWidget(self.label_title)

        self.vbox.addWidget(self.cover_label)
        self.vbox.addLayout(hbox1)

        # -------------------------------------------------

        self.manga_list_widget = QListWidget()
        self.manga_list_widget.setIconSize(self.icon_size)
        self.manga_list_widget.setViewMode(QListWidget.IconMode)
        self.manga_list_widget.setMovement(QListWidget.Static)
        self.manga_list_widget.setResizeMode(QListWidget.Adjust)
        self.manga_list_widget.installEventFilter(self)
        self.manga_list_widget.setWordWrap(True)
        self.manga_list_widget.doubleClicked.connect(self.ml_double_clicked)

        self.chapter_list_view = QTableView(self)
        self.chapter_list_view.doubleClicked.connect(self.cl_double_clicked)
        self.chapter_model = ChapterModel()
        self.chapter_list_view.setModel(self.chapter_model)
        self.chapter_list_view.horizontalHeader().setResizeMode(QHeaderView.Stretch)
        self.chapter_list_view.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.chapter_split_page = QSplitter(Qt.Horizontal)
        self.chapter_split_page.addWidget(self.chapter_list_view)
        self.chapter_split_page.setStretchFactor(0, 10)

        self.update_manga_list_widget()

        vbox_widget = QWidget()
        vbox_widget.setLayout(self.vbox)
        self.splitter.addWidget(vbox_widget)
        self.stacked = QStackedWidget()
        self.stacked.addWidget(self.manga_list_widget)
        self.stacked.addWidget(self.chapter_split_page)
        info_widget = QWidget()
        info_widget.setLayout(self.vbox)
        self.splitter.addWidget(info_widget)
        self.splitter.addWidget(self.stacked)
        self.splitter.setStretchFactor(0, 10)


        # self.main_widget = QStackedWidget()
        # self.main_widget.addWidget(self.manga_list_widget)
        # self.main_widget.addWidget(self.chapter_split_page)
        # self.setCentralWidget(self.main_widget)
        self.setCentralWidget(self.splitter)

        self.setGeometry(100, 100, 800, 800)
        self.define_global_shortcut()

    def define_global_shortcut(self):
        sequence = {
            'Q': self.close,
            'Backspace': self.page_to_manga_list,
        }

        for key, value in sequence.items():
            s = QShortcut(QKeySequence(key), self, value)
            s.setEnabled(True)
            self.global_shortcuts.append(s)

    def eventFilter(self, obj, event):
        # http://stackoverflow.com/questions/11379816/qlistview-in-gridmode-auto-stretch-with-fixed-items-on-a-row-column
        if obj is self.manga_list_widget and event.type() == event.Resize:
            padding = 15 * 2
            div = self.manga_list_widget.width() / (self.icon_size.width() + padding)
            width = self.manga_list_widget.width() / div
            div = self.manga_list_widget.height() / self.icon_size.height()
            height = self.manga_list_widget.height() / div
            grid_size = QSize(width, height)
            self.manga_list_widget.setGridSize(grid_size)
        return super(MainWindowRedesign, self).eventFilter(obj, event)

    def ml_double_clicked(self, index):
        item = self.manga_list_widget.currentItem()
        title = item.text()
        manga = Library.create_manga_from_db_by_title(title)
        self.update_chapter_list_widget(manga)
        self.page_to_chapter_list()

    def cl_double_clicked(self, index):
        pass

    def page_to_manga_list(self):
        self.main_widget.setCurrentWidget(self.manga_list_widget)

    def page_to_chapter_list(self):
        self.main_widget.setCurrentWidget(self.chapter_split_page)

    # def closeEvent(self, event):
    #     # Checking to see if the user wants to quit
    #     quit_msg = 'Are you sure you want to Quit?'
    #     reply = QMessageBox.question(self, 'Close Application', quit_msg, QMessageBox.Yes, QMessageBox.No)
    #     if reply == QMessageBox.No:
    #         event.ignore()
    #         return
    #     Library.close()
    #     bg_file_io.join()
    #     event.accept()

    def update_manga_list_widget(self):
        cursor = Library.db.cursor()

        query = "SELECT title, cover_url FROM manga ORDER BY title"
        cursor.execute(query)

        data_query_result = cursor.fetchall()

        for data in data_query_result:
            title = data[0]
            image_data = web_utility.download_image_from_src(data[1])
            image = Image.open(image_data)
            image.thumbnail((self.icon_size.width(), self.icon_size.height()), Image.ANTIALIAS)
            image = round_corners(image, 10)
            icon = QIcon(QPixmap.fromImage(ImageQt.ImageQt(image).copy()))
            item = QListWidgetItem(title, self.manga_list_widget)
            item.setStatusTip(title)
            # item.setBackgroundColor(QColor('#A6A6A6'))
            item.setIcon(icon)

    def update_chapter_list_widget(self, manga):
        table = []
        for chapter in manga.chapter_list:
            table.append([chapter.title, chapter.number, chapter.completed, chapter.downloaded])
        self.chapter_model.update(table)