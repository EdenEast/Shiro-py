__author__ = 'Athena'

from abc import ABCMeta, abstractmethod


class BaseSite(metaclass=ABCMeta):

    @abstractmethod
    def get_name(self):
        pass

    @abstractmethod
    def create_manga_from_url(self, url):
        pass

    @abstractmethod
    def update_manga(self, manga):
        pass

    @abstractmethod
    def download_chapter(self, chapter):
        pass