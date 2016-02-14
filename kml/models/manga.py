__author__ = 'Athena'


class Manga(object):
    def __init__(self, title, manga_site, url):
        self.title = title
        self.manga_site = manga_site
        self.url = url
        self.current_chapter_index = 0
        self.last_chapter_read = 0
        self.chapter_list = []

    # ----------------------------------------------------------------------------------
    # Updating
    def check_for_updates(self):
        pass

    def add_chapter(self, chapter):
        self.chapter_list.append(chapter)

    def remove_chapter(self, chapter):
        self.chapter_list.remove(chapter)

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

    def get_number_of_chapters(self):
        return len(self.chapter_list)

    # ----------------------------------------------------------------------------------
    # Setters
    def set_last_chapter_read(self, chapter_number):
        if chapter_number in range(len(self.chapter_list) - 1):
            self.last_chapter_read = chapter_number

    def set_current_chapter_index(self, chapter_index):
        if chapter_index in range(len(self.chapter_list) - 1):
            self.current_chapter_index = chapter_index