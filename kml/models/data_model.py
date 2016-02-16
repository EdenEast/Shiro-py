__author__ = 'Athena'

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class MangaListViewModel(QAbstractListModel):
    def __init__(self, data_in=[], parent=None, *args):
        # Calling the base class constructor
        QAbstractListModel.__init__(self, parent, *args)
        self._data = data_in


    def data(self, index, role):
        if role == Qt.DisplayRole:
            return self._data[index.row()]
        # if not index.isValid():
        #     return QVariant()
        # elif role != Qt.DisplayRole:
        #     return QVariant()

    def rowCount(self, parent):
        return len(self._data)

    def setData(self, index, value, roll=Qt.EditRole):
        if roll == Qt.EditRole:
            self._data[index] = value
            # self.dataChanged.emit(index, value)

    def insertRow(self, position, rows, QModelIndex_parent=None):
        self.beginInsertRows(QModelIndex_parent, position, position + rows - 1)
        for i in range(rows):
            self._data.insert(position, '')
        self.endInsertRows()


    def sort(self, order):
        self.emit(SIGNAL("layoutAboutToBeChanged()"))
        self._data = sorted(self._data)
        if order == Qt.DescendingOrder:
            self._data.reverse()
        self.emit(SIGNAL("layoutChanged()"))

    # def add_row(self, value):
    #     self.insertRow(self.rowCount(), 1, QModelIndex())
    #     self.setData(self.rowCount() - 1, value)
    def addRow(self, value):
        index = QModelIndex()
        size = len(self._data)
        if size == 0:
            size = 0
        else:
            size -= 1
        self.insertRow(size, 1, index)
        self.setData(size, value, Qt.EditRole)
        self.sort(Qt.AscendingOrder)

class ChapterTableViewModel(QAbstractTableModel):
    header_data = ['Chapter Number', 'Title', 'Completed', 'Downloaded']

    def __init__(self, data_in=[], parent=None, *args):
        # Calling the base class constructor
        QAbstractListModel.__init__(self, parent, *args)
        self._data = data_in
        self._header_data = ChapterTableViewModel.header_data

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        if len(self._data) == 0:
            return 0
        return len(self._data[0])

    def data(self, index, role=None):
        if role == Qt.DisplayRole:
            return self._data[index.row()][index.column()]
        elif role == Qt.BackgroundColorRole:
            row = self._data[index.row()]
            if row[2] == True:
                return QColor('#77dd77')
            elif row[3] == False:
                return QColor('#ff4040')
            elif row[2] == False and row[3] == True:
                # return QColor('#C9A0DC')
                return QColor('#9BDDFF')
        elif role == Qt.TextAlignmentRole:
            return Qt.AlignCenter
        else:
            return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return self._header_data[section]
            else:
                return ''
        return QAbstractTableModel.headerData(self, section, orientation, role)

    def setData(self, index, value, role=Qt.EditRole):
        if role == Qt.EditRole:
            self._data[index] = value

    # def addRow(self, value):
    #     self._data.append(value)
    #     self.layoutChanged.emit()