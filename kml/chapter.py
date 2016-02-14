__author__ = 'Athena'


import os

class Chapter(object):
    def __init__(self, name, directory, initial_page=0):
        self.name = name
        self.directory = directory
        self.current_page_index = initial_page
        self.pages = []

    def add_page(self, page):
        self.pages.append(page)

    def remove_page(self, page):
        self.pages.remove(page)

    def get_current_page(self):
        return self.current_page_index

    def get_current_page_title(self):
        return self.pages[self.current_page_index].title

    def get_current_page_number(self):
        return self.pages[self.current_page_index].number

    def go_next_page(self):
        if self.current_page_index < self.get_number_of_pages() - 1:
            self.current_page_index += 1

    def go_prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1

    def go_first_page(self):
        self.current_page_index = 0

    def go_last_page(self):
        self.current_page_index = self.get_number_of_pages() - 1

    def set_current_page(self, index):
        if index in range(self.get_number_of_pages()):
            self.current_page_index = index

    def get_path(self):
        return os.path.join(self.directory, self.name)

    def get_number_of_pages(self):
        return len(self.pages)