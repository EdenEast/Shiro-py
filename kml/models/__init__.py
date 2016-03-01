import hashlib


def hash_string(string):
    m = hashlib.md5()
    m.update(str.encode(string))
    h = int(m.hexdigest(), 16) & 0xFFFFFFFFFFFFFF
    # print('{} : {}'.format(string, h))
    return h


class Manga(object):
    def __init__(self, hash_data, title, url, description, cover_url, site):
        self.hash = hash_data
        self.title = title
        self.url = url
        self.description = description
        self.cover_url = cover_url
        self.site = site
        self.chapter_list = []

    def add_chapter(self, chapter):
        self.chapter_list.append(chapter)

    def remove_chapter(self, chapter):
        self.chapter_list.remove(chapter)

    def get_chapter_by_title(self, title):
        for chapter in self.chapter_list:
            if chapter.title == title:
                return chapter
        return None

    # This function will take the current chapter that the library is on and return the next one
    def next_chapter(self, chapter):
        index = self.chapter_list.index(chapter)
        if index < len(self.chapter_list) - 1:
            return self.chapter_list[index + 1]
        return chapter

    # This function will take the current chapter that the library is on and return the prev chapter
    def prev_chapter(self, chapter):
        index = self.chapter_list.index(chapter)
        if index > 0:
            return self.chapter_list[index - 1]
        return chapter


class Chapter(object):
    def __init__(self, title, url, number, sub_number, downloaded, completed, parent):
        self.title = title
        self.url = url
        self.number = number
        self.sub_number = sub_number
        self.downloaded = downloaded
        self.completed = completed
        self.parent = parent

    def __lt__(self, other):
        return float(self.get_number_string()) < float(other.get_number_string())

    def get_number_string(self):
        if self.sub_number == '0' or self.sub_number == 0:
            return self.number
        return str(self.number) + '.' + str(self.sub_number)

    def get_file_name(self):
        l = len(str(self.number))
        diff = 3 - l
        if diff < 0:
            diff = 0
        s = '0' * diff + str(self.number)
        if self.sub_number > 0:
            s += '.' + str(self.sub_number)
        s += ' {}.zip'.format(self.parent.title)
        return s