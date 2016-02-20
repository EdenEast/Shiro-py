__author__ = 'Athena'

from PyQt4.QtCore import QAbstractListModel, QAbstractTableModel, QModelIndex, Qt, SIGNAL
from PyQt4.QtGui import QColor
import bisect

class MangaListViewModel(QAbstractListModel):
    def __init__(self, data_in=[], parent=None, *args):
        QAbstractListModel.__init__(self, parent, *args)
        self._data = data_in

    def data(self, index, int_role=None):
        if int_role == Qt.DisplayRole:
            return self._data[index.row()].title
        return None

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self._data)

    def setData(self, index, value, int_role=Qt.EditRole):
        if int_role == Qt.EditRole:
            self._data[index] = value
            self.dataChanged.emit(index, index)

    def insertRows(self, position, rows, parent=None, *args, **kwargs):
        self.beginInsertRows(parent, position, position + rows - 1)
        for i in range(rows):
            self._data.insert(position, '')
        self.endInsertRows()

    def insertRow(self, position, parent=None, *args, **kwargs):
        self.beginInsertRows(parent, position, 1)
        self._data.insert(position, '')
        self.endInsertRows()

    def sort(self, order):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._data = sorted(self._data)
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    def add_row(self, value):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        bisect.insort_left(self._data, value)
        self.emit(SIGNAL("layoutChanged()"))
        # size = len(self._data)
        # self.beginInsertRows(QModelIndex(), size - 1, size - 1)
        # self._data.insert(size - 1, value)
        # self.endInsertRows()


class ChapterListViewModel(QAbstractTableModel):
    header_data = ['Chapter Number', 'Title', 'Completed', 'Downloaded']

    def __init__(self, data_in=[], parent=None, *args):
        QAbstractTableModel.__init__(self, parent, *args)
        self.items = data_in

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            col = index.column()
            if col == 0:
                return self.items[index.row()].get_number_string()
            elif col == 1:
                return self.items[index.row()].title
            elif col == 2:
                return self.items[index.row()].get_complete_string()
            elif col == 3:
                return self.items[index.row()].get_download_string()
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        elif role == Qt.BackgroundColorRole:
            row_data = self.items[index.row()]
            if row_data.completed:
                return QColor('#77dd77')
            elif not row_data.downloaded:
                return QColor('#ff4040')
            elif not row_data.completed and row_data.downloaded:
                # return QColor('#C9A0DC')
                return QColor('#9BDDFF')


        return None

    def rowCount(self, parent=None, *args, **kwargs):
        return len(self.items)

    def columnCount(self, parent=None, *args, **kwargs):
        if self.rowCount() == 0:
            return 0
        return 4

    def headerData(self, section, orientation, role=None):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self.header_data[section]
            else:
                return ''

    def setData(self, index, value, role=None):
        if role == Qt.EditRole:
            self.items[index.row()] = value
            self.dataChanged.emit(index, index)

    def add_row(self, value):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        bisect.insort_left(self.items, value)
        self.emit(SIGNAL("layoutChanged()"))

    def remove_row(self, value):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.items.remove(value)
        self.emit(SIGNAL("layoutChanged()"))

    def set_data(self, data):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self.items = data
        self.emit(SIGNAL("layoutChanged()"))

