from PyQt4 import QtGui, QtCore

class UpdateWindow(QtGui.QWidget):
    def __init__(self, parent, worker=None, size=(500, 400)):
        super(UpdateWindow, self).__init__()
        self._parent = parent
        self.worker = worker
        self.setWindowTitle('Update')
        self.text_edit = QtGui.QTextEdit()
        self.text_edit.setReadOnly(True)
        self.font = QtGui.QFont("Monospace");
        self.font.setStyleHint(QtGui.QFont.TypeWriter)
        self.text_edit.setFont(self.font)
        self.button = QtGui.QPushButton('Close')
        self.button.pressed.connect(self.close)
        self.button.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.vbox = QtGui.QVBoxLayout(self)
        self.vbox.addWidget(self.text_edit)
        self.vbox.addWidget(self.button)
        self.resize(size[0], size[1])
        self.connect(QtGui.QShortcut(QtGui.QKeySequence('Return'), self), QtCore.SIGNAL('activated()'), self.close)

    def set_worker(self, worker):
        self.worker = worker

    def set_text(self, text):
        self.text_edit.setText(text)

    def append_text(self, text):
        data = self.text_edit.document().toPlainText()
        data += text
        self.text_edit.setText(data)

    def closeEvent(self, event):
        self.worker.abort()
        self.worker.wait()
