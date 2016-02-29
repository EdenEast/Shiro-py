

from kml.web import web_utility
from PIL import Image
import configparser
import os
import sqlite3

from kml.web.site import mangalife
from kml import models


class Library(object):
    db = None
    directory = ''
    covers = {}
    site_list = {}

    def __init__(self):
        self.init_site_list()

    @staticmethod
    def init_site_list():
        Library.site_list[mangalife.MangaLife.get_name()] = mangalife.MangaLife(Library)

    @staticmethod
    def load():
        if not os.path.isfile('settings.ini'):
            # @TODO: Create a dialgue box that asks for the library folder and save it in the settings.ini file
            print('[ERROR] There is no settings.ini file')
            return

        config = configparser.ConfigParser()
        config.read('settings.ini')
        Library.directory = os.path.normpath(config['Library']['library_directory'])

        # Checking to see if there is a library.db file in the library directory
        data_base_file = os.path.join(Library.directory, 'Library.db')
        if not os.path.isfile(data_base_file):
            # If there is no database file then need to create one
            Library.db = sqlite3.connect(data_base_file)
            cursor = Library.db.cursor()
            cursor.execute("""CREATE TABLE manga
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    url BLOB NOT NULL,
    cover_url BLOB NOT NULL,
    site TEXT NOT NULL
)"""
                           )
            cursor.execute("""CREATE TABLE chapter
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    url BLOB NOT NULL,
    number DECIMAL NOT NULL,
    prim_number INTEGER NOT NULL,
    sub_number INTEGER NOT NULL,
    downloaded BOOLEAN NOT NULL CHECK(downloaded IN (0, 1)) DEFAULT 0,
    completed BOOLEAN NOT NULL CHECK(completed IN (0, 1)) DEFAULT 0,
    manga_id INTEGER NOT NULL REFERENCES manga(id)
)"""
                           )
            Library.db.commit()
        else:
            Library.db = sqlite3.connect(data_base_file)

        # Checking to see if there is a '.Cover' folder in the library directory
        cover_folder = os.path.join(Library.directory, '.Cover')
        if not os.path.isdir(cover_folder):
            os.mkdir(cover_folder)

        files = os.listdir(cover_folder)
        for file in files:
            title = file.rsplit('/', 1)[0].split('.')[0]
            image = Image.open(os.path.join(cover_folder, file))
            image.thumbnail((200, 350))
            Library.covers[title] = image
        return

    @staticmethod
    def close():
        Library.db.close()

    @staticmethod
    def add_manga(manga):
        cursor = Library.db.cursor()

        # Is the manga already in the database?
        cursor.execute('SELECT id FROM manga WHERE id={}'.format(manga.hash))
        data = cursor.fetchone()
        if data is not None:
            print('{} already exists in the library database'.format(manga.title))
            return

        # The manga is not part of the database and needs to be added
        cmd = 'INSERT INTO manga (id, title, description, url, cover_url, site) VALUES' \
              '({}, \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')'.format(manga.hash, manga.title, manga.description,
                                                                    manga.url, manga.cover_url, manga.site)
        cursor.execute(cmd)

        # Adding the chapters to the chapter table
        new_query = True
        cmd = ''
        for c in manga.chapter_list:
            if new_query:
                cmd = 'INSERT INTO chapter(title, url, number, prim_number, sub_number,' \
                          ' downloaded, completed, manga_id)'
                new_query = False
            else:
                cmd += ' UNION'

            cmd += " SELECT \'{}\', \'{}\', {}, {}, {}, {}, {}, {}".format(
                c.title, c.url, float(c.get_number_string()), c.number, c.sub_number,
                int(c.downloaded), int(c.completed), c.parent.hash)
        cursor.execute(cmd)
        Library.db.commit()

        # Take added Manga and download the Cover image into the cover folder
        cover_file = os.path.join(Library.directory, '.Cover', '{}.jpg'.format(manga.title))
        if not os.path.isfile(cover_file):
            web_utility.download_image(cover_file, manga.cover_url)
        image = Image.open(cover_file)
        image.thumbnail((200, 350))
        Library.covers[manga.title] = image

    @staticmethod
    def remove_manga(manga):
        cursor = Library.db.cursor()
        cursor.execute('DELETE FROM manga WHERE id={}'.format(manga.hash))
        for chapter in manga.chapter_list:
            cursor.execute('DELETE FROM chapter WHERE manga_id={} AND title=\'{}\''.format(manga.hash, chapter.title))
        Library.db.commit()

    @staticmethod
    def create_manga_from_db_by_title(title):
        cursor = Library.db.cursor()
        cursor.execute('SELECT * FROM manga WHERE title = \'{}\''.format(title))
        data = cursor.fetchone()
        if data is None:
            return None

        manga = models.Manga(data[0], data[1], data[3], data[2], data[4], data[5])

        # Selecting all of the chapters of the manga
        cursor.execute('SELECT * FROM chapter WHERE manga_id = {} ORDER BY number'.format(manga.hash))
        data = cursor.fetchall()
        for d in data:
            chapter = models.Chapter(d[1], d[2], int(d[4]), int(d[5]), (d[6] == 1), (d[7] == 1), manga)
            manga.add_chapter(chapter)
        return manga
