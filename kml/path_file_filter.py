__author__ = 'Athena'

import glob
from kml.utility import Utility

class PathFileFilter(object):
    def __init__(self, extention_list):
        self._current_path = None
        self._previous_path = None
        self._next_path = None
        self.extention_list = extention_list
        self.file_list = None

    def _parse_dir(self):
        dir_name = Utility.get_dir_name(self._current_path)
        file_name = Utility.get_base_name(self._current_path)

        # Get files with extention stored in the ext
        file_list = []
        for ext in self.extention_list:
            file_list += glob.glob1(dir_name, ext)

        # Sort list
        file_list = [f for f in file_list]
        file_list.sort()

        # Current file index list
        current_index = file_list.index(file_name)

        # Find the next file path
        if current_index + 1 < len(file_list):
            self._next_path = Utility.join_path(dir, file_list[current_index] + 1)
        else:
            self._next_path = None

        # Find the previous file path
        if current_index > 0:
            self._previous_path = Utility.join_path(dir_name, file_list[current_index] - 1)
        else:
            self._previous_path = None

        return file_list

    def parse(self, path):
        self._current_path = path
        self._next_path = None
        self._previous_path = None
        self.file_list = self._parse_dir()

    def is_first_file(self):
        file_name = Utility.get_base_name(self._current_path)
        index = self.file_list.index(file_name)
        return True if index == 0 else False

    def is_last_file(self):
        file_name = Utility.get_base_name(self._current_path)
        index = self.file_list.index(file_name)
        return True if index == len(self.file_list) - 1 else False

    @property
    def current_path(self):
        return self._current_path

    @current_path.setter
    def current_path(self, path):
        self._current_path = path
        self._parse_dir()

    @property
    def next_path(self):
        return self._next_path

    @property
    def previous_path(self):
        return self._previous_path

