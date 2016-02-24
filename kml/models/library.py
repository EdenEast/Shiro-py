__author__ = 'Athena'

from kml.models.gui_data_models import MangaListViewModel
from kml.models.manga import Manga, Chapter
from kml.web.site import mangalife
from configparser import ConfigParser
from bs4 import BeautifulSoup
from PIL import Image
import os

class Library(object):
    def __init__(self):
        self.manga_list = []
        self.site_list = {}
        self.covers = {}
        self.libray_directory = ''
        self.manga_model = MangaListViewModel()
        self.init_site_list()

    def init_site_list(self):
        self.site_list['MangaLife'] = mangalife.MangaLife()

    def load_library(self):
        if not os.path.isfile('settings.ini'):
            print('[ERROR] There is no settings.ini file')
            return

        config = ConfigParser()
        config.read('settings.ini')
        self.libray_directory = os.path.normpath(config['Library']['library_directory'])

        # Checking to see if there is a 'library.dat' file
        library_path_file = os.path.join(self.libray_directory, 'library.dat')
        if not os.path.isfile(library_path_file):
            # Since that there is not a library file then the library folder is blank and we are done
            return

        with open(library_path_file, 'r') as file:
            data = file.read()

        soup = BeautifulSoup(data, 'html.parser')

        for mt in soup.findAll('manga'):
            title = mt.get('title')
            url = mt.get('url')
            manga_site = mt.get('manga_site')
            manga = Manga(title, url, manga_site)

            for c in mt.select('chapter'):
                chapter_title = c.get('title')
                chapter_url = c.get('url')
                chapter_number = c.get('number')
                chapter_sub_number = c.get('sub_number')
                chapter_completed = c.get('completed') == 'True'
                chapter_downloaded = c.get('downloaded') == 'True'
                chapter = Chapter(manga, chapter_title, chapter_url, chapter_number,
                                  chapter_sub_number, chapter_downloaded, chapter_completed)
                manga.add_chapter(chapter)
                # TODO: add chapter to manga table view model

            # Adding the manga to the list of manga and the model
            # @CHECK if we just link the data of the library list of mangas to the listview model does adding to the
            # manga list also add it to the model? (like it is a pointer to the list)
            self.manga_list.append(manga)
            self.manga_model.add_row(manga)

            # Checking the Cover folder for a Cover with the manga's title on it
            cover_file_path = os.path.join(self.libray_directory, '.Cover', (manga.title + '.jpg'))
            if os.path.isfile(cover_file_path):
                image = Image.open(cover_file_path)
                image.thumbnail((200, 350), Image.ANTIALIAS)
                self.covers[manga.title] = image

    def save_library(self):
        file_name = 'library.dat'

        # This will be the concatenation of all of the manga's xml information
        text = ''

        for manga in self.manga_list:
            text += manga.to_xml()

        # If we want BeautifulSoup to prettify the output html/xml then set prettify to true
        prettify = False
        if prettify:
            soup = BeautifulSoup(text, 'html.parser')
            text = soup.prettify()

        path = os.path.join(self.libray_directory, file_name)
        with open(path, 'w') as output:
            output.write(text)
            output.close()

    def add_manga(self, manga):
        # Checking to see if the manga is part of the manga list
        duplicate = False
        for m in self.manga_list:
            if m.title == manga.title:
                duplicate = True
                break

        if duplicate:
            print('[ERROR] The manga is already in the list')
            return

        self.manga_list.append(manga)
        self.manga_model.add_row(manga)
        # @CHECK add to model if it does not point like i am thinking it might
        self.manga_list.sort(key=lambda x: x.title, reverse=False)

    def remove_manga(self, manga):
        self.manga_list.remove(manga)

    def get_manga_by_title(self, title):
        for manga in self.manga_list:
            if manga.title == title:
                return manga
        return None


