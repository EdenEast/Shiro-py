from shiro.web import web_utility
from PIL import Image
import configparser
import os
import sqlite3
import shutil

from shiro.web.site import mangalife
from shiro import models


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
    def get_settings_file_name():
        home_directory = os.path.expanduser('~')
        return os.path.join(home_directory, 'shiro.ini')

    @staticmethod
    def load():
        settings_file = Library.get_settings_file_name()
        if not os.path.isfile(Library.get_settings_file_name()):
            # @TODO: Create a dialgue box that asks for the library folder and save it in the settings.ini file
            print('[ERROR] There is no {} file'.format(settings_file))
            return False

        config = configparser.ConfigParser()
        config.read(settings_file)
        Library.directory = os.path.normpath(config['Library']['library_directory'])

        # Checking to see if there is a library.db file in the library directory
        data_base_file = os.path.join(Library.directory, 'Library.db')
        if not os.path.isfile(data_base_file):
            # If there is no database file then need to create one
            Library.db = sqlite3.connect(data_base_file, check_same_thread=False)
            cursor = Library.db.cursor()
            cursor.execute("""CREATE TABLE manga
(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT NOT NULL,
    genre TEXT NOT NULL,
    authors TEXT NOT NULL,
    year INTEGER NOT NULL,
    url BLOB NOT NULL,
    cover_url BLOB NOT NULL,
    publish_status TEXT NOT NULL,
    scan_status TEXT NOT NULL,
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
            Library.db = sqlite3.connect(data_base_file, check_same_thread=False)

        # Checking to see if there is a '.Cover' folder in the library directory
        cover_folder = os.path.join(Library.directory, '.Cover')
        if not os.path.isdir(cover_folder):
            os.mkdir(cover_folder)

        files = os.listdir(cover_folder)
        for file in files:
            title = file.rsplit('/', 1)[0].split('.')[0]
            image = Image.open(os.path.join(cover_folder, file))
            # image.thumbnail((200, 350))
            Library.covers[title] = image
        return True

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
        cmd = "INSERT INTO manga (id, title, description, genre, authors, year, url, cover_url, publish_status," \
              " scan_status, site) VALUES ({}, '{}', '{}', '{}', '{}', {}, '{}', '{}', '{}', '{}', '{}')".format(
                manga.hash, manga.title, manga.description, manga.get_genre_string(), manga.get_author_string(),
                manga.year, manga.url, manga.cover_url, manga.publish_status, manga.scan_status, manga.site.get_name()
                )
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

            cmd += " SELECT '{}', '{}', {}, {}, {}, {}, {}, {}".format(
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

        # Adding an info file to the manga folder
        text = 'title={}\nurl={}\ncover_url={}\nauthor={}\nyear={}\ndescription={}\genre={}\n' \
               'publish_status={}\nscan_status={}\nsite={}\n'.format(
                manga.title, manga.url, manga.cover_url, manga.get_author_string(), manga.year, manga.description,
                manga.get_genre_string(), manga.publish_status, manga.scan_status, manga.site.get_name()
                )
        manga_folder = os.path.join(Library.directory, manga.title)
        if not os.path.isdir(manga_folder):
            os.mkdir(manga_folder)
        info_title = os.path.join(manga_folder, manga.title + '.info')
        with open(info_title, 'w') as info:
            info.write(text)

    @staticmethod
    def remove_manga(manga):
        cursor = Library.db.cursor()
        cursor.execute('DELETE FROM manga WHERE id={}'.format(manga.hash))
        for chapter in manga.chapter_list:
            cursor.execute('DELETE FROM chapter WHERE manga_id={} AND title=\'{}\''.format(manga.hash, chapter.title))
        Library.db.commit()
        folder = os.path.join(Library.directory, manga.title)
        if os.path.isdir(folder):
            shutil.rmtree(folder)

    @staticmethod
    def create_manga_from_db_by_title(title):
        cursor = Library.db.cursor()
        cursor.execute("SELECT * FROM manga WHERE title = '{}'".format(title))
        data = cursor.fetchone()
        if data is None:
            return None

        genre = data[3].split(',')
        authors = data[4].split(',')

        manga = models.Manga(data[0], data[1], data[6], data[2], authors, data[5], data[7],
                             Library.site_list[data[10]], data[8], data[9], genre)

        # Selecting all of the chapters of the manga
        cursor.execute('SELECT * FROM chapter WHERE manga_id = {} ORDER BY number'.format(manga.hash))
        data = cursor.fetchall()
        for d in data:
            chapter = models.Chapter(d[1], d[2], int(d[4]), int(d[5]), (d[6] == 1), (d[7] == 1), manga)
            manga.add_chapter(chapter)
        return manga

    @staticmethod
    def update_manga_by_title(title):
        cursor = Library.db.cursor()
        manga = Library.create_manga_from_db_by_title(title)

        folder = os.path.join(Library.directory, manga.title)
        if not os.path.isdir(folder):
            os.mkdir(folder)

        # updating the manga
        updated_chapter_list, status_changed = manga.site.update_manga(manga)

        if status_changed:
            cursor.execute("UPDATE manga SET publish_status=?, scan_status=? WHERE id=?",
                           (manga.publish_status, manga.scan_status, manga.hash))
            text = 'title={}\nurl={}\ncover_url={}\nauthor={}\nyear={}\ndescription={}\genre={}\n' \
                'publish_status={}\nscan_status={}\nsite={}\n'.format(
                    manga.title, manga.url, manga.cover_url, manga.get_author_string(), manga.year, manga.description,
                    manga.get_genre_string(), manga.publish_status, manga.scan_status, manga.site.get_name()
                )
            manga_folder = os.path.join(Library.directory, manga.title)
            info_title = os.path.join(manga_folder, manga.title + '.info')
            with open(info_title, 'w') as info:
                info.write(text)

        size = len(updated_chapter_list)
        if size <= 0:
            return updated_chapter_list

        batch_count = 0
        batch_size = 50
        new_query = True
        cmd = ''
        for c in updated_chapter_list:
            if new_query:
                cmd = 'INSERT INTO chapter(title, url, number, prim_number, sub_number,' \
                          ' downloaded, completed, manga_id)'
                new_query = False
            else:
                cmd += ' UNION'

            cmd += " SELECT '{}', '{}', {}, {}, {}, {}, {}, {}".format(
                c.title, c.url, float(c.get_number_string()), c.number, c.sub_number, int(c.downloaded),
                int(c.completed), c.parent.hash
            )
            batch_count += 1
            if batch_count == batch_size:
                cursor.execute(cmd)
                Library.db.commit()
                new_query = True
                batch_count = 0

        if batch_count != 0:
            cursor.execute(cmd)
            Library.db.commit()

        return updated_chapter_list
