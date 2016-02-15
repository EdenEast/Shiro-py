__author__ = 'Athena'

from kml.web import web_utility
from kml.models.manga import Manga
from kml.models.chapter import Chapter

import urllib
from io import BytesIO, StringIO
import zipfile


class MangaLife(object):
    _BASE_URL = 'http://manga.life'
    _DIRECTORY_URL = 'http://manga.life/directory/'
    _SEARCH_URL = 'http://manga.life/advanced-search/result.php?sortBy=alphabet&direction=' \
                  'ASC&textOnly=no&resPerPage=20&page=1&seriesName='

    def get_name(self):
        return 'MangaLife'

    def create_manga_from_url(self, url):
        # soup = web_utility.get_soup_from_url(url)
        soup = web_utility.get_pretty_soup_from_url(url)

        # Getting the title of the manga
        title = soup.find('title').text
        title = title.split(' Manga - Read')[0]

        # Create the new Manga object
        manga = Manga(title, self.get_name(), url)

        # Finding all of the chapter links
        raw_link_list = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-9 > a')

        # Going through all of the chapters and creating each chapter
        for link in raw_link_list:
            # Getting the href of the chapter
            href = MangaLife._BASE_URL + link.get('href')
            if '/page-' in href:
                href = href.split('/page-')[0]

            # Finding the chapter number and seeing if there is a sub number
            raw_number = href.split('/chapter-')[1].split('/index-')[0]
            number = sub_number = '0'

            # Checking to see if the raw_number has a decimal point
            if '.' in raw_number:
                number, sub_number = raw_number.split('.')[0]
            else:
                number = raw_number

            # Getting the chapter title and cleaning it up. Also @CHECK: do I have to remove ':' character?
            chapter_title = link.text.rstrip().lstrip()

            chapter = Chapter(manga, chapter_title, href, int(number), int(sub_number))
            manga.add_chapter(chapter)
        manga.sort_chapters()
        return manga

    def update_manga(self, manga):
        # Checking to see if the manga came from this site
        if manga.manga_site != self.get_name():
            print('[ERROR ', self.get_name(), '] Cannot update ', manga.title, ' it is from ', manga.manga_site)
            return None

        soup = web_utility.get_soup_from_url(manga.url)

        # Getting the list of chapter links
        raw_link_list = soup.select('div.col-lg-9.col-md-9.col-sm-9.col-xs-9 > a')

        # Checking to see if the are any new chapters that are not in the list
        number_new_chapters = len(raw_link_list) - len(manga.chapter_list)
        if number_new_chapters == 0:
            return None

        new_chapter_count = 0
        for link in raw_link_list:
            # Getting the chapter title
            chapter_title = link.text.rstrip().lstrip()
            if not manga.is_in_chapter_list(chapter_title):
                href = MangaLife._BASE_URL + link.get('href')
                if '/page-' in href:
                    href = href.split('/page-')[0]

                raw_number = href.split('/chapter-')[1].split('/index-')[0]
                number = sub_number = '0'
                if '.' in raw_number:
                    number, sub_number = raw_number.split('.')[0]
                else:
                    number = raw_number
                chapter = Chapter(manga, chapter_title, href, int(number), int(sub_number))
                new_chapter_count += 1
                manga.add_chapter(chapter)
        manga.sort_chapters()

    def download_chapter(self, chapter):
        soup = web_utility.get_soup_from_url(chapter.url)

        images = []
        image_links = soup.findAll('img')
        for image in image_links:
            src = image.get('src')
            name = src.rsplit('/', 1)[1]
            download_image = urllib.request.urlopen(src)
            images.append([download_image, name])

        # Testing to see if the images are downloading
        # @NOTE: This works :) !!!!!!!!!!!!!!!!!!!!!!!
        buffer = BytesIO()
        zip_file = zipfile.ZipFile(buffer, 'w')

        for i in range(len(images)):
            zip_file.writestr(images[i][1], images[i][0].read())

        zip_file.close()

        output = open('test_image_zip_file.zip', 'wb')
        output.write(buffer.getvalue())
        output.close()
        buffer.close()

        return images
