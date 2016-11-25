
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
    _BASE_URL = 'http://mangalife.org'
    _DIRECTORY_URL = 'http://mangalife.org/directory/'
    # _SEARCH_URL = 'http://manga.life/search/?q='
    _SEARCH_URL = 'http://mangalife.org/search/?keyword=room'
    _SITE_NAME = 'MangaLife'

    def __init__(self, library):
        self.library = library


    @staticmethod
    def get_name():
        return MangaLife._SITE_NAME

    def create_manga_info_from_url(self, url):
        soup, html = web_utility.get_soup_from_url(url)

        # Getting the title of the series
        title = soup.find('title').text.replace(' Manga For Free  | MangaLife', '')
        title = title.split(' ', 1)[1]
        title = re.sub("[\':]", '', title)

        # Getting the description of the series
        description = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12 span div div div')[0].text
        description = description.replace('\'', '').replace('\"', '')

        header_links = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12 span div > div > a')

        # Getting all of the genera links
        genera_list = []
        authors = []
        year = 0
        scan_status = ''
        publish_status = ''
        for link in header_links:
            href = link.get('href')
            if '?genre=' in href:
                genera_list.append(link.text)
            elif '?year=' in href:
                year = link.text
            elif '?author=' in href:
                authors.append(link.text)
            elif '?type=' in href:
                manga_type = link.text
            elif '?status=' in href:
                scan_status = self.parse_status(link.text)
            elif '?pstatus':
                publish_status = self.parse_status(link.text)

        # Checking if it has an alternative name
        info_header = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12  span div > div')
        if 'Alternate Name(s):' in str(info_header[0]):
            alternative_names = info_header[0].text.split('Alternate Name(s):  ')[1].rstrip('\n\t')

        # Getting the cover_image
        cover_url = soup.select('div.col-lg-3.col-md-3.col-sm-3.hidden-xs.leftImage > img')[0].get('src')

        # Creating the manga object
        manga = Manga(hash_string(title), title, url, description, authors, int(year), cover_url, self,
                      publish_status, scan_status, genera_list)

        # Finding all of the chapters
        chapter_link_list = soup.select('body > div.container.mainContainer > div > div.list.chapter-list > a')

        # Going though all of the chapters
        for link in chapter_link_list:
            # Getting chapter link
            href = self._BASE_URL + link.get('href').replace('-page-1', '')

            # Finding the chapter number
            raw_number = link.get('chapter')
            number = sub_number = '0'
            if '.' in raw_number:
                number, sub_number = raw_number.split('.')
            else:
                number = raw_number

            chapter_title = link.span.text

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
        status_changed = False

        soup, html = web_utility.get_soup_from_url(manga.url)

        # Getting Publishing Authors and year Scanlation Status
        scan_status = ''
        publish_status = ''
        header_links = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-12 span div > div > a')
        for link in header_links:
            href = link.get('href')
            if '?status=' in href:
                scan_status = self.parse_status(link.text)
            elif '?pstatus':
                publish_status = self.parse_status(link.text)

        if manga.publish_status != publish_status or manga.scan_status != scan_status:
            status_changed = True
            manga.publish_status = publish_status
            manga.scan_status = scan_status

        chapter_collection = soup.select('body > div.container.mainContainer > div > div.list.chapter-list > a')
        chapter_collection.reverse()
        chapter_collection_size = len(chapter_collection)

        # Getting the number of chapters from the database
        db_chapter_count = len(manga.chapter_list)

        if db_chapter_count == chapter_collection_size:
            return [], status_changed

        # Getting the size difference of the site and the database
        delta = chapter_collection_size - db_chapter_count

        # Looping through the difference and adding them all to the database
        index = db_chapter_count

        for i in range(delta):
            link = chapter_collection[index]
            href = self._BASE_URL + link.get('href').replace('-page-1', '')

            raw_number = link.get('chapter')
            if '.' in raw_number:
                number, sub_number = raw_number.split('.')
            else:
                number = raw_number
                sub_number = '0'

            title = link.span.text
            chapter = Chapter(title, href, int(number), int(sub_number), False, False, manga)

            updated_chapter_list.append(chapter)
            manga.add_chapter(chapter)
            index += 1
        return updated_chapter_list, status_changed

    def download_chapter(self, chapter):
        file_path = os.path.join(self.library.directory, chapter.parent.title, chapter.get_file_name())

        # Checking to see if the file is already there
        if os.path.isfile(file_path):
            return

        soup, html = web_utility.get_soup_from_url(chapter.url)
        images = []
        image_links = soup.select('div.image-container > div > img')
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
        image_links = soup.select('div.image-container > div > img')
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
        image_links = soup.select('div.image-container > div > img')
        for link in image_links:
            src = link.get('src')
            result.append(src)
        return result

    def get_list_search_results(self, search_term):
        result = []
        search_term = search_term.lower()
        soup, html = web_utility.get_soup_from_url('http://mangalife.org/directory/')
        directory_link_list = soup.select('a.ttip')
        for link in directory_link_list:
            text = link.text
            if search_term in text.lower():
                href = MangaLife._BASE_URL + link.get('href')
                result.append((text, href, self))
        return result

    def parse_status(self, status):
        lower = status.lower()
        if 'ongoing' in lower:
            return 'Ongoing'
        if 'incomplete' in lower:
            return 'Incomplete'
        if 'complete' in lower:
            return 'Completed'
        if 'hiatus' in lower:
            return 'Hiatus'
        if 'cancel' in lower:
            return 'Canceled'
        if 'discontinue' in lower:
            return 'Discontinue'
        if 'unfinished' in lower:
            return 'Unfinished'
