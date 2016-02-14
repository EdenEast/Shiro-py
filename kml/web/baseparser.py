__author__ = 'Athena'


class BaseParser(object):
    def __init__(self):
        self.manga_urls = {}
        self.chapter_urls = {}
        self.page_urls = {}
        self.image_urls = {}

    def update_manga_list(self):
        pass

    def update_chapter_list(self, manga_name):
        pass

    def update_page_url(self, chapter_name):
        pass

    def update_image_url(self, page_url):
        pass