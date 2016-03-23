
from shiro.web import web_utility
from shiro import bg_file_io
from shiro.models import Manga, Chapter, hash_string
from io import BytesIO
import threading
import os
import re
import urllib
import zipfile


class MangaLife(object):
    _BASE_URL = 'http://manga.life'
    _DIRECTORY_URL = 'http://manga.life/directory/'
    _SEARCH_URL = 'http://manga.life/search/?q='
    _SITE_NAME = 'MangaLife'

    def __init__(self, library):
        self.library = library


    @staticmethod
    def get_name():
        return MangaLife._SITE_NAME

    def create_manga_info_from_url(self, url):
        soup, html = web_utility.get_soup_from_url(url)

        # Getting the title of the series
        # title = soup.title
        title = soup.find('title').text
        title = title.split('- Read ')[1].split(' Online Free')[0]
        title = re.sub("[\':]", '', title)
        # title = title.replace('\'', '')

        # Getting the description of the series
        description = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12 span div div div')[0].text
        description = description.replace('\'', '').replace('\"', '')

        # Getting all of the genera links
        genera_collection = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12 span div > div > a.dark_link')
        genera_list = []
        for link in genera_collection:
            genera_list.append(link.text)

        # Getting Publishing Authors and year Scanlation Status
        info_links = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12  span div > div')
        if 'Alternate Names: ' in str(info_links[0]):
            publish_status = info_links[3].text.rstrip().lstrip().split(': ')[1]
            scan_status = info_links[4].text.rstrip().lstrip().split(': ')[1]
            authors_text = info_links[2].text.rstrip().lstrip()
        else:
            publish_status = info_links[2].text.rstrip().lstrip().split(': ')[1]
            scan_status = info_links[3].text.rstrip().lstrip().split(': ')[1]
            authors_text = info_links[1].text.rstrip().lstrip()

        year = authors_text.split('(', 1)[-1].rsplit(')', 1)[0]
        authors_text = authors_text.split('Author: ')[1].split('(', 1)[0]
        authors = authors_text.split(', ')

        # Getting the cover_image
        cover_url = soup.select('body > div.container.container-main > div.well > div.row >'
                                ' div.col-lg-3.col-md-3.col-sm-3.hidden-xs > img')[0].get('src')

        # Create the image url from the manga url ang the cover url that i am given
        ext = cover_url.rsplit('.', 1)[1]
        cover_src = '{}/{}.{}'.format(cover_url.rsplit('/', 1)[0], url.rsplit('/', 1)[1], ext)

        # Creating the manga object
        manga = Manga(hash_string(title), title, url, description, authors, int(year), cover_url, self,
                      publish_status, scan_status, genera_list)

        # Finding all of the chapters
        chapter_link_list = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-9 > a')

        # Going though all of the chapters
        for link in chapter_link_list:
            # Getting chapter link
            href = self._BASE_URL + link.get('href')
            if '/page-' in href:
                href = href.split('/page-')[0]
            # Finding the chapter number
            raw_number = href.split('/chapter-')[1].split('/index-')[0]
            number = sub_number = '0'
            if '.' in raw_number:
                number, sub_number = raw_number.split('.')
            else:
                number = raw_number

            chapter_title = link.text.rstrip().lstrip()

            chapter = Chapter(chapter_title, href, int(number), int(sub_number), False, False, manga)
            manga.add_chapter(chapter)
        manga.chapter_list.sort()
        return manga

    # @TODO: return the chapters that have been added to the manga along with the new manga object as a tulip. Then the
    # library will update the database and the site is not responsible for it. Then the site will not need a reference
    # to the library and will not have to pass it in. @NOTE @DOME
    def update_manga(self, manga):
        if manga.site.get_name() is not self.get_name():
            print('[ERROR {}] Cannot update {} as it is from {}'.format(self.get_name(), manga.title, manga.site))
            return None

        updated_chapter_list = []

        soup, html = web_utility.get_soup_from_url(manga.url)

        chapter_collection = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-9 > a')
        chapter_collection.reverse()
        chapter_collection_size = len(chapter_collection)

        # Getting the number of chapters from the database
        db_chapter_count = len(manga.chapter_list)

        if db_chapter_count == chapter_collection_size:
            return []

        # Getting the size difference of the site and the database
        delta = chapter_collection_size - db_chapter_count

        # Looping through the difference and adding them all to the database
        index = db_chapter_count

        for i in range(delta):
            link = chapter_collection[index]
            href = self._BASE_URL + link.get('href')
            if '/page-' in href:
                href = href.split('/page-')[0]
            raw_number = href.split('/chapter-')[1].split('/index-')[0]
            if '.' in raw_number:
                number, sub_number = raw_number.split('.')
            else:
                number = raw_number
                sub_number = '0'
            title = link.text.rstrip().lstrip()
            chapter = Chapter(title, href, int(number), int(sub_number), False, False, manga)
            updated_chapter_list.append(chapter)
            manga.add_chapter(chapter)
            index += 1
        return updated_chapter_list

    def download_chapter(self, chapter):
        file_path = os.path.join(self.library.directory, chapter.parent.title, chapter.get_file_name())

        # Checking to see if the file is already there
        if os.path.isfile(file_path):
            return

        soup, html = web_utility.get_soup_from_url(chapter.url)
        images = []
        image_links = soup.findAll('img')
        for image in image_links:
            src = image.get('src')
            name = src.rsplit('/', 1)[1]
            download_image = urllib.request.urlopen(src)
            images.append([download_image, name])
        buffer = BytesIO()
        zip_file = zipfile.ZipFile(buffer, 'w')
        # for i in range(len(images)):
        #     zip_file.writestr((images[i][1], images[i][0].read()))
        for i in images:
            zip_file.writestr(i[1], i[0].read())

        # Saving the information on the chapter
        info_text = '[Info]\nmanga={}\ntitle={}\nurl={}\nnumber={}\nsub_number={}\nmanga_site={}\n'.format(
            chapter.parent.title, chapter.title, chapter.url, str(chapter.number),
            str(chapter.sub_number), self.get_name()
        )
        zip_file.writestr('info.ini', info_text)
        zip_file.close()

        # Checking to see if the folder exists
        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        output = open(file_path, 'wb')
        output.write(buffer.getvalue())
        output.close()
        buffer.close()

    def download_chapter_threaded(self, chapter):
        file_path = os.path.join(self.library.directory, chapter.parent.title, chapter.get_file_name())

        folder = os.path.dirname(file_path)
        if not os.path.exists(folder):
            os.makedirs(folder)

        if os.path.isfile(file_path):
            return

        soup, html = web_utility.get_soup_from_url(chapter.url)
        thread_list = []
        images = []
        lock = threading.Lock()
        image_links = soup.findAll('img')
        for link in image_links:
            t = threading.Thread(target=web_utility.download_image_link, args=(link, images, lock))
            t.daemon = True
            t.start()
            thread_list.append(t)

        for thread in thread_list:
            thread.join()

        # Saving the information on the chapter
        info_text = '[Info]\nmanga={}\ntitle={}\nurl={}\nnumber={}\nsub_number={}\nmanga_site={}\n'.format(
            chapter.parent.title, chapter.title, chapter.url, str(chapter.number),
            str(chapter.sub_number), self.get_name()
        )

        bg_file_io.push(bg_file_io.save_to_archive, (images, file_path, info_text))

    def get_all_pages_from_chapter(self, url):
        result = []
        soup, html = web_utility.get_soup_from_url(url)
        image_links = soup.findAll('img')
        for link in image_links:
            src = link.get('src')
            result.append(src)
        return result

    def get_list_search_results(self, search_term):
        ret = []
        search_term = search_term.replace(' ', '+')
        soup, html = web_utility.get_soup_from_url(MangaLife._SEARCH_URL + search_term)
        search_result_hl = soup.select('body > div.container.container-main > div > '
                                       'div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div.well > h1')
        if search_result_hl:
            links = soup.select('#content > p > a')
            for link in links:
                url = MangaLife._BASE_URL + link.get('href').replace('..', '')
                title = link.text
                ret.append([title, url, self])
        else:
            title_tag = soup.select('div.col-lg-8.col-md-8.col-sm-8.col-xs-12 > h1')
            title = title_tag[0].text
            chapters = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-9 > a')[0]
            href = MangaLife._BASE_URL + chapters.get('href').replace('..', '').split('/chapter-')[0]
            ret.append([title, href, self])
        return ret
