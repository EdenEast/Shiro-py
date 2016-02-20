__author__ = 'Athena'

from kml.models.gui_data_models import ChapterListViewModel

class Manga(object):
    def __init__(self, title, url, manga_site):
        self.title = title
        self.url = url
        self.manga_site = manga_site
        self.chapter_list = []
        self.current_chapter_index = 0

    def __lt__(self, other):
        return self.title < other.title

    # ----------------------------------------------------------------------------------
    # Updating
    def check_for_updates(self):
        pass

    def add_chapter(self, chapter):
        self.chapter_list.append(chapter)

    def remove_chapter(self, chapter):
        self.chapter_list.remove(chapter)

    def is_in_chapter_list(self, chapter):
        for c in self.chapter_list:
            if c == chapter:
                return True
        return False

    def sort_chapters(self):
        self.chapter_list.sort(key=lambda x: x.number, reverse=False)

    # ----------------------------------------------------------------------------------
    # Moving to next and previous chapters
    def next_chapter(self):
        if self.current_chapter_index <= len(self.chapter_list) - 1:
            self.current_chapter_index += 1
            return self.get_current_chapter()
        return None

    def prev_chapter(self):
        if self.current_chapter_index > 0:
            self.current_chapter_index -= 1
            return self.get_current_chapter()
        return None

    # ----------------------------------------------------------------------------------
    # Getters
    def get_current_chapter(self):
        return self.chapter_list[self.current_chapter_index]

    def get_number_of_chapter(self):
        return len(self.chapter_list)

    def get_chapter_by_title(self, title):
        for chapter in self.chapter_list:
            if chapter.title == title:
                return chapter
        return None

    # ----------------------------------------------------------------------------------
    # Setters
    def set_current_chapter_index(self, chapter_index):
        if chapter_index in range(self.get_number_of_chapter() - 1):
            self.current_chapter_index = chapter_index

    # ----------------------------------------------------------------------------------
    # XML
    def to_xml(self):
        # This function will return the manga object as an xml string
        s = '<manga title=\"{}\" manga_site=\"{}\" url=\"{}\">\n'.format(self.title, self.manga_site, self.url)
        s += '<manga_information current_chapter_index=\"{}\" />\n' \
            .format(self.current_chapter_index)
        s += '    <chapters>\n'
        for chapter in self.chapter_list:
            s += '        ' + chapter.to_xml()
        s += '    </chapters>\n'
        s += '</manga>\n'
        return s

class Chapter(object):
    def __init__(self, parent, title, url, number, sub_number, downloaded=False, completed=False):
        self.parent = parent
        self.title = title
        self.url = url
        self.number = number
        self.sub_number = sub_number
        self.downloaded = downloaded
        self.completed = completed
        self.pages = []
        self.current_page_index = 0

    def __lt__(self, other):
        return float(self.get_number_string()) < float(other.get_number_string())

    # ----------------------------------------------------------------------------------
    # Page interactions
    def add_page(self, page):
        self.pages.append(page)

    def remove_page(self, page):
        self.pages.remove(page)

    def next_page(self):
        if self.current_page_index <= self.get_number_of_pages() - 1:
            self.current_page_index += 1
            return self.get_current_page()
        return None

    def prev_page(self):
        if self.current_page_index > 0:
            self.current_page_index -= 1
            return self.get_current_page()
        return None

    def first_page(self):
        self.current_page_index = 0
        return self.get_current_page()

    def last_page(self):
        self.current_page_index = self.get_number_of_pages() - 1
        return self.get_current_page()

    # ----------------------------------------------------------------------------------
    # Getters
    def get_current_page(self):
        return self.current_page_index

    def get_number_of_pages(self):
        return len(self.pages)

    def get_number_string(self):
        if self.sub_number != '0':
            return self.number + '.' + self.sub_number
        return self.number

    def get_download_string(self):
        if self.downloaded:
            return 'Yes'
        return 'No'

    def get_complete_string(self):
        if self.completed:
            return 'Yes'
        return 'No'

    # ----------------------------------------------------------------------------------
    # XML
    def to_xml(self):
        s = '<chapter title=\"{}\" url=\"{}\" number=\"{}\" sub_number=\"{}\" downloaded=\"{}\" completed=\"{}\"/>\n'\
            .format(self.title, self.url, self.number, self.sub_number, self.downloaded, self.completed)
        return s


class Page(object):
    def __init__(self, parent, data, title, number):
        self.parent = parent
        self.data = data
        self.title = title
        self.number = number


