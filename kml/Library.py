

from kml.web import web_utility
from PIL import Image
import configparser
import os
import sqlite3

from kml.web.site import mangalife


class Library(object):
    def __init__(self):
        self.manga_list = {}
        self.site_list = {}
        self.covers = {}
        self.db = None
        self.directory = ''
        self.init_site_list()

    def init_site_list(self):
        self.site_list['MangaLife'] = mangalife.MangaLife(self)

    def load(self):
        if not os.path.isfile('settings.ini'):
            print('[ERROR] There is no settings.ini file')
            return

        config = configparser.ConfigParser()
        config.read('settings.ini')
        self.directory = os.path.normpath(config['Library']['library_directory'])

        # Checking to see if there is a library.db file
        data_base_file = os.path.join(self.directory, 'Library.db')

        if not os.path.isfile(data_base_file):
            # If there is no db file then we have to create a fresh database file
            db = sqlite3.connect(data_base_file)
            self.db = db

            cursor = db.cursor()
            cursor.execute("""CREATE TABLE manga
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    url BLOB NOT NULL,
    cover_url BLOB NOT NULL,
    site TEXT NOT NULL
)""")

#             cursor.execute("""CREATE TABLE chapter
# (
#     id INTEGER PRIMARY KEY AUTOINCREMENT,
#     title TEXT NOT NULL,
#     url BLOB NOT NULL,
#     number INTEGER NOT NULL,
#     sub_number INTEGER NOT NULL,
#     downloaded BOOLEAN NOT NULL CHECK(downloaded IN (0, 1)) DEFAULT 0,
#     completed BOOLEAN NOT NULL CHECK(completed IN (0, 1)) DEFAULT 0,
#     manga_id INTEGER NOT NULL,
#     FOREIGN KEY(manga_id) REFERENCES manga(id)
# )""")
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
)""")
            db.commit()
        else:
            self.db = sqlite3.connect(data_base_file)

        # Checking to see if the folder has a '.Cover' folder
        cover_folder = os.path.join(self.directory, '.Cover')
        if not os.path.isdir(cover_folder):
            os.mkdir(cover_folder)

        files = os.listdir(cover_folder)
        for file in files:
            title = file.rsplit('/', 1)[0].split('.')[0]
            image = Image.open(os.path.join(cover_folder, file))
            image.thumbnail((200, 350))
            self.covers[title] = image
        return

    def add_manga(self, manga):
        # Checking to see if the manga is already in the library db
        cursor = self.db.cursor()
        cursor.execute('SELECT id FROM manga WHERE id={}'.format(manga.hash))
        data = cursor.fetchone()
        if data is not None:
            print('{} already exists in the library'.format(manga.title))
            return

        # If we are here then it is not a part of the library database and we should add it
        command = "INSERT INTO manga (id, title, description, url, cover_url, site) VALUES" \
                  "({}, \'{}\', \'{}\', \'{}\', \'{}\', \'{}\')".format(manga.hash, manga.title, manga.description,
                                                         manga.url, manga.cover_url, manga.site)
        cursor.execute(command)
        # Now adding the chapters to the chapter table
        new_query = True
        command = ''
        for chapter in manga.chapter_list:
            if new_query:
                command = 'INSERT INTO chapter(title, url, number, prim_number, sub_number,' \
                          ' downloaded, completed, manga_id)'
                new_query = False
            else:
                command += ' UNION'

            command += " SELECT \'{}\', \'{}\', {}, {}, {}, {}, {}, {}".format(
                chapter.title, chapter.url, float(chapter.get_number_string()), chapter.number, chapter.sub_number,
                int(chapter.downloaded), int(chapter.completed), chapter.parent.hash)
        cursor.execute(command)
        self.db.commit()

        # Now that the manga is added to the library we need to download the cover image and save it in the cover folder
        cover_file = os.path.join(self.directory, '.Cover', '{}.jpg'.format(manga.title))
        if not os.path.isfile(cover_file):
            # Need to download the Cover image
            web_utility.download_image(cover_file, manga.cover_url)
        image = Image.open(cover_file)
        image.thumbnail((200, 350))
        self.covers[manga.title] = image

    def create_manga_from_db_by_title(self, title):
        # Finding the manga by the title
        cursor = self.db.cursor()
        cursor.execute('SELECT * FROM manga WHERE title=\'{}\''.format(title))
        data = cursor.fetchone()

        # Could not find the title in the database
        if data is None:
            return None

        hash_data = data[0]
        manga = mangalife.Manga(hash_data, title, data[3], data[2], data[4], data[5])

        # Selecting all of the chapters of the manga
        cursor.execute('SELECT * FROM chapter WHERE manga_id={} ORDER BY NUMBER'.format(hash_data))
        data = cursor.fetchall()
        for d in data:
            chapter = mangalife.Chapter(d[1], d[2], int(d[4]), int(d[5]), (d[6] == 1), (d[7] == 1), manga)
            manga.add_chapter(chapter)
        return manga
