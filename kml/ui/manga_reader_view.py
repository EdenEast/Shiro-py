__author__ = 'Athena'

from PyQt4 import QtGui, QtCore
from kml.widget.kscrollviewer import KScrollAreaViewer

# import os
# import sys

class MainWindowView(QtGui.QMainWindow):
    def __init__(self, controller):
        super(MainWindowView, self).__init__()

        # Initializing the ui for the main window
        self.setup_ui()

        # Saving a reference to the main window controller
        self.controller = controller

        self.global_shortcuts = []

        # Completing setup and configuration of the main window
        self._create_actions()
        self._create_connections(controller)
        self._define_global_shortcuts(controller)
        self.reset_window_default_size()
        self._centralize_window()

    def setup_ui(self):
        self.label = QtGui.QLabel(self)
        self.label.setAlignment(QtCore.Qt.AlignCenter)

        self.current_view_container = KScrollAreaViewer(self)
        self.current_view_container.setBackgroundRole(QtGui.QPalette.Dark)
        self.current_view_container.setWidget(self.label)
        self.current_view_container.setAlignment(QtCore.Qt.AlignCenter)
        self.setCentralWidget(self.current_view_container)

    # Creating menu actions
    def _create_actions(self):
        self.action_open = QtGui.QAction(QtGui.QIcon('icon.png'), '&Open', self)
        self.action_open.setShortcut('Ctrl+O')
        self.action_open.setStatusTip('Open Chapter file (.zip)')

        self.action_open_online = QtGui.QAction(QtGui.QIcon('icon.png'), '&Open Online', self)
        self.action_open_online.setShortcut('Ctrl+Shift+O')
        self.action_open_online.setStatusTip('Open Chapter From Web')

        self.action_next_page = QtGui.QAction('&Next Page', self)
        self.action_next_page.setShortcut('n')
        self.action_next_page.setStatusTip('Moves the viewer to the next page')

        self.action_prev_page = QtGui.QAction('&Previous Page', self)
        self.action_prev_page.setShortcut('p')
        self.action_prev_page.setStatusTip('Moves the viewer to the previous page')

        self.action_first_page = QtGui.QAction('&First Page', self)
        self.action_first_page.setShortcut('b')
        self.action_first_page.setStatusTip('Moves the viewer to the first page')

        self.action_last_page = QtGui.QAction('&Last Page', self)
        self.action_last_page.setShortcut('l')
        self.action_last_page.setStatusTip('Moves the viewer to the last page')

        self.action_rotate_left = QtGui.QAction('&Rotate Left', self)
        self.action_rotate_left.setShortcut('Ctrl+l')
        self.action_rotate_left.setStatusTip('Rotate page left')

        self.action_rotate_right = QtGui.QAction('&Rotate Right', self)
        self.action_rotate_right.setShortcut('Ctrl+r')
        self.action_rotate_right.setStatusTip('Rotate page right')

        self.action_next_chapter = QtGui.QAction('&Next Chapter', self)
        self.action_next_chapter.setShortcut('Ctrl+n')
        self.action_next_chapter.setStatusTip('Moves the viewer to the next chapter')

        self.action_prev_chapter = QtGui.QAction('&Previous Chapter', self)
        self.action_prev_chapter.setShortcut('Ctrl+p')
        self.action_prev_chapter.setStatusTip('Moves the viewer to the previous chapter')

        self.action_original_fit = QtGui.QAction('&Original View', self)
        self.action_original_fit.setShortcut('Ctrl+1')
        self.action_original_fit.setStatusTip('Original size of the page')

        self.action_vertical_fit = QtGui.QAction('&Vertical View', self)
        self.action_vertical_fit.setShortcut('Ctrl+2')
        self.action_vertical_fit.setStatusTip('Fit page vertically')

        self.action_horizontal_fit = QtGui.QAction('&Horizontal View', self)
        self.action_horizontal_fit.setShortcut('Ctrl+3')
        self.action_horizontal_fit.setStatusTip('Fit page horizontally')

        self.action_best_fit = QtGui.QAction('&Best Fit', self)
        self.action_best_fit.setShortcut('Ctrl+4')
        self.action_best_fit.setStatusTip('Finds the best fit for the page')

        self.action_go_to_page = QtGui.QAction('&Go to page', self)
        self.action_go_to_page.setShortcut('Ctrl+g')
        self.action_go_to_page.setStatusTip('Go to page')

        self.action_close = QtGui.QAction('&Close', self)
        self.action_close.setShortcut('Ctrl+Q')
        self.action_close.setStatusTip('Close Application')

    # ----------------------------------------------------------------------------------
    # Linking actions in the view to the logic of the controller
    def _create_connections(self, controller):
        self.action_open.triggered.connect(controller.open)
        self.action_open_online.triggered.connect(controller.open_online)

        self.action_next_page.triggered.connect(controller.next_page)
        self.action_prev_page.triggered.connect(controller.prev_page)

        self.action_first_page.triggered.connect(controller.first_page)
        self.action_last_page.triggered.connect(controller.last_page)
        self.action_next_chapter.triggered.connect(controller.next_chapter)
        self.action_prev_chapter.triggered.connect(controller.prev_chapter)
        self.action_go_to_page.triggered.connect(controller.go_to_page)

        self.action_rotate_left.triggered.connect(controller.rotate_left)
        self.action_rotate_right.triggered.connect(controller.rotate_right)

        self.action_group_view = QtGui.QActionGroup(self)
        self.action_group_view.addAction(self.action_original_fit)
        self.action_group_view.addAction(self.action_vertical_fit)
        self.action_group_view.addAction(self.action_horizontal_fit)
        self.action_group_view.addAction(self.action_best_fit)

        self.action_original_fit.triggered.connect(controller.origninal_fit)
        self.action_vertical_fit.triggered.connect(controller.vertical_fit)
        self.action_horizontal_fit.triggered.connect(controller.horizontal_fit)
        self.action_best_fit.triggered.connect(controller.best_fit)

        self.action_close.triggered.connect(controller.exit)

    # ----------------------------------------------------------------------------------
    # Defining all of the global shortcuts and linking them to the controller logic
    def _define_global_shortcuts(self, controller):
        squence = {
            'Ctrl+Shift+Left': controller.prev_chapter,
            'Ctrl+Left': controller.first_page,
            'Left': controller.prev_page,
            'Right': controller.next_page,
            'Ctrl+Right': controller.last_page,
            'Ctrl+Shift+Right': controller.next_chapter,
            'Ctrl+R': controller.rotate_right,
            'Ctrl+Shift+R': controller.rotate_left,
            'Ctrl+O': controller.open,
            '1': controller.origninal_fit,
            '2': controller.vertical_fit,
            '3': controller.horizontal_fit,
            '4': controller.best_fit,
        }

        for key, value in squence.items():
            s = QtGui.QShortcut(QtGui.QKeySequence(key), self.current_view_container, value)
            s.setEnabled(True)
            self.global_shortcuts.append(s)

    # ----------------------------------------------------------------------------------
    # Centers the application in the middle of the users desktop screen
    # def _centralize_window(self):
    #     screen = QtGui.QDesktopWidget().screenGeometry()
    #     size = self.geometry()
    #     x_center = (screen.width() - size.width()) / 2
    #     y_center = (screen.height() - size.height()) / 2
    #     self.move(x_center, y_center)
    #     self.setMinimumSize(QtGui.QApplication.desktop().screenGeometry().size() * 0.8)

    def _centralize_window(self):
        # center window from http://stackoverflow.com/questions/20243637/pyqt4-center-window-on-active-screen
        frame_geometry = self.frameGeometry()
        monitor_screen = QtGui.QApplication.desktop().screenNumber(QtGui.QApplication.desktop().cursor().pos())
        center_point = QtGui.QApplication.desktop().screenGeometry(monitor_screen).center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())

    def reset_window_default_size(self):
        self.setMinimumSize(QtGui.QApplication.desktop().screenGeometry().size() * 0.8)

    def get_current_view_container_size(self):
        return self.current_view_container.size()

    def set_viewer_content(self, content):
        # if content and isinstance(QtGui.QPixmap):
        if content:
            if isinstance(content, QtGui.QPixmap):
                self.label.setPixmap(content)
                self.label.resize(content.size())
                self.current_view_container.reset_scroll_position()

    # ----------------------------------------------------------------------------------
    # Update the current view content and resize to the new content
    def update_current_view_container_size(self):
        self.set_viewer_content(self.controller.model.get_current_page())

    # ----------------------------------------------------------------------------------
    # Handle Full screen event
    def on_action_fullscreen_triggered(self):
        if self.isFullScreen():
            # show menubar, toolbar, statusbar, etc...
            self.showMaximized()

            for sc in self.global_shortcuts:
                sc.setEnabled(False)
        else:
            # hide menubar, toolbar, statusbar, etc...
            self.showFullScreen()
            for sc in self.global_shortcuts:
                sc.setEnabled(True)

    # ----------------------------------------------------------------------------------
    # Exit action
    def on_action_exit_triggered(self):
        super(MainWindowView, self).close()
        self.controller.exit()

    # ----------------------------------------------------------------------------------
    # User input and Window Events
    def keyPressEvent(self, event):
        if event.key() == QtCore.Qt.Key_F:
            self.on_action_fullscreen_triggered()
        if event.key() == QtCore.Qt.Key_N:
            self.controller.next_page()
        if event.key() == QtCore.Qt.Key_P:
            self.controller.prev_page()

        # pass the event down the inheritance tree
        super(MainWindowView, self).keyPressEvent(event)

    def mouseDoubleClickEvent(self, *args, **kwargs):
        if args[0].button() == QtCore.Qt.LeftButton:
            self.on_action_fullscreen_triggered()
        super(MainWindowView, self).mouseDoubleClickEvent(*args, **kwargs)

    def resizeEvent(self, *args, **kwargs):
        self.update_current_view_container_size()
        super(MainWindowView, self).resizeEvent(*args, **kwargs)




