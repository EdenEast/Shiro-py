
# Importing the view and model for the main window
from kml import main_window_view, main_window_model, utility
from PyQt4 import QtGui, QtCore


class MainWindowController(object):
    def __init__(self):
        self.view = main_window_view.MainWindowView(self)
        self.model = main_window_model.MainWindowModel(self)
        # self.model.open('D:\\manga\\Horimiya\\018 Chapter 18.zip')

        # Create recent file manager, preferences, and settings

    @QtCore.pyqtSlot()
    def open(self):
        file_path = QtGui.QFileDialog().getOpenFileName(
            self.view, self.view.tr('Open Chapter File'),
            self.model.current_directory,
            self.view.tr(
                'All supported files (*.zip *.cbz *.rar *.cbr *.tar *.cbt);; '
                'Zip Files (*.zip *.cbz);; Rar Files (*.rar *.cbr);; '
                'Tar Files (*.tar *.cbt);; All files (*)'
            )
        )
        if file_path:
            self.load(file_path)

    def load(self, file_name, initial_page=0):
        file_name = str(file_name)
        try:
            self.model.open(file_name)
            self.set_view_content(self.model.get_current_page())
            self.view.set_viewer_content(self.model.get_current_page())

            self.model.current_directory = utility.Utility.get_dir_name(file_name)
        except:
            QtGui.QMessageBox().warning(self.view, self.view.tr('Error'),
                                        self.view.tr('Error loading file' + file_name), QtGui.QMessageBox.Close)

    def save_image(self):
        pass

    def open_online(self):
        pass

    # ----------------------------------------------------------------------------------
    # Interacting with pages

    def next_page(self):
        # Getting the value of the current vertical scroll bar and checking to see
        # if it is at the end/bottom
        value = self.view.current_view_container.verticalScrollBar().value()
        maximum = self.view.current_view_container.verticalScrollBar().maximum()

        if value == maximum:
            self.model.next_page()
            return

        # If we are not at the end of the page we need to move down the page
        # Get the page step value from the scroll bar
        page_step = self.view.current_view_container.verticalScrollBar().pageStep()
        page_step -= (page_step * 0.1)
        self.view.current_view_container.verticalScrollBar().setValue(value + page_step)

    def prev_page(self):
        # Getting the value of the current vertical scroll bar and checking to see
        # if the value is a 0 and we are at the top of the page
        value = self.view.current_view_container.verticalScrollBar().value()

        if value == self.view.current_view_container.verticalScrollBar().minimum():
            self.model.prev_page()
            self.view.current_view_container.verticalScrollBar().setValue(
                self.view.current_view_container.verticalScrollBar().maximum()
            )
            return

        # If we are not at the beginning of the page we need to move the page up
        page_step = self.view.current_view_container.verticalScrollBar().pageStep()
        page_step -= (page_step * 0.1)
        self.view.current_view_container.verticalScrollBar().setValue(value - page_step)

    def first_page(self):
        # @ChangeMe: this functionality will be moved to the chapter object
        self.model.current_page = 0
        self.view.set_viewer_content(self.model.get_current_page())

    def last_page(self):
        # @ChangeMe: this functionality will be moved to the chapter object
        self.model.current_page = len(self.model.page_list) - 1
        self.view.set_viewer_content(self.model.get_current_page())

    def go_to_page(self, page_number):
        # @ChangeMe: this functionality will be moved to the chapter object
        if page_number < len(self.model.page_list) - 1 and page_number > 0:
            self.model.current_page = page_number
            self.view.set_viewer_content(self.model.get_current_page())

    def next_chapter(self):
        # @Wrong: this is not page but change chapters entirly this is wrong
        # @Note: model has not implmeneted next_chapter
        self.model.next_page()

    def prev_chapter(self):
        # @Wrong: this is not page but change chapters entirly this is wrong
        self.model.prev_page()

    def _update_navigation_actions(self):
        pass

    def rotate_left(self):
        self.model.rotate_left()

    def rotate_right(self):
        self.model.rotate_right()

    def origninal_fit(self):
        self.model.original_fit()

    def vertical_fit(self):
        self.model.vertical_fit()

    def horizontal_fit(self):
        self.model.horizontal_fit()

    def best_fit(self):
        self.model.best_fit()

    # ----------------------------------------------------------------------------------
    # Update and load functions

    def load_recent_file(self):
        pass

    def update_bookmark_menu(self):
        pass

    def preference_dialog(self):
        pass

    def exit(self):
        pass

    def show(self):
        self.view.show()

    def get_current_view_container_size(self):
        pass

    def set_view_content(self, content):
        self.view.set_viewer_content(content)
        self.update_status_bar()

    def update_status_bar(self):
        pass