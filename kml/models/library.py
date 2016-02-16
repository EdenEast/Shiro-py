__author__ = 'Athena'

from kml.models.manga import Manga
from kml.models.chapter import Chapter
from kml.models.data_model import MangaListViewModel
from configparser import ConfigParser
from bs4 import BeautifulSoup
import os

class Library(object):
    def __init__(self):
        self.manga_list = []
        self.site_list = []
        self.library_directory = ''
        self.manga_list_model = MangaListViewModel()

    def load_library(self):
        # Reading the settings file and getting the library directory
        if not os.path.isfile('settings.ini'):
            print('[ERROR]: There is no settings.ini file')
            return

        config = ConfigParser()
        config.read('settings.ini')
        self.library_directory = config['Library']['library_directory']
        self.library_directory = os.path.normpath(self.library_directory)

        # Checking to see if there is a library file
        self.library_file_path = os.path.join(self.library_directory, 'library.dat')

        # If there is not a library file then the library is empty and we dont have to load anything
        if not os.path.isfile(self.library_file_path):
            return

        # @TODO: Load the library here
        with open(self.library_file_path, 'r') as input:
            data = input.read()

        soup = BeautifulSoup(data, 'html.parser')

        manga_tags = soup.findAll('manga')
        for mt in manga_tags:
            title = mt.get('title')
            url = mt.get('url')
            manga_site = mt.get('manga_site')

            manga = Manga(title, manga_site, url)

            chapters = mt.select('chapter')
            for c in chapters:
                chapter_title = c.get('title')
                chapter_url = c.get('url')
                chapter_number = int(c.get('number'))
                chapter_sub_number = int(c.get('sub_number'))
                chapter_completed = c.get('completed') == 'True'
                chapter_downloaded = c.get('downloaded') == 'True'

                chapter = Chapter(manga, chapter_title, chapter_url, chapter_number,
                                  chapter_sub_number, 0, chapter_downloaded, chapter_completed)
                manga.add_chapter(chapter)

            self.add_manga(manga)

    def save_library(self):
        library_file_name = 'library.dat'

        # This will be the concatenation of all the manga's xml information
        text = ''

        # looping through all of the manga objects in the list
        for manga in self.manga_list:
            text += manga.to_xml()

        soup = BeautifulSoup(text, 'html.parser')

        # Now save the text to the library_file_name
        with open(os.path.join(self.library_directory, library_file_name), 'w') as output:
            # output.write(soup.prettify(formatter='html'))
            output.write(text)
            output.close()

    def add_manga(self, manga):
        # Checking to see if the manga is part of the manga list
        duplicate = False
        for m in self.manga_list:
            if manga.title == m.title:
                duplicate = True
                break
        if duplicate:
            print('[ERROR]: The manga is already in the list')
            return
        self.manga_list.append(manga)
        self.manga_list_model.addRow(manga.title)
        self.manga_list.sort(key=lambda x: x.title, reverse=False)

    def remove_manga(self, manga):
        self.manga_list.remove(manga)

    def get_manga_by_title(self, title):
        for manga in self.manga_list:
            if manga.title == title:
                return manga
        return None

