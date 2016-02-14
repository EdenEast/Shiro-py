__author__ = 'Athena'

import os

class Utility(object):
    @staticmethod
    def get_file_extention(file_name):
        return os.path.splitext(file_name)[1]

    @staticmethod
    def get_dir_name(file_path):
        return os.path.dirname(file_path)

    @staticmethod
    def get_base_name(file_name):
        return os.path.basename(file_name)

    @staticmethod
    def get_parent_path(file_path):
        return os.path.split(os.path.abspath(os.path.dirname(file_path)))[0]

    @staticmethod
    def join_path(root, directory, file):
        return os.path.join(root, directory, file)

    def join_path(self, directory, file):
        return os.path.join(directory, file)

    @staticmethod
    def path_exist(file_path):
        return os.path.lexists(file_path)

    @staticmethod
    def file_exist(file_path):
        return os.path.exists(file_path)

    @staticmethod
    def is_dir(directory):
        return os.path.isdir(directory)

    @staticmethod
    def get_home_dir():
        return os.path.expanduser('~')

    @staticmethod
    def convert_string_to_boolean(string):
        if string == 'True':
            return True
        elif string == 'False':
            return False
        else:
            raise ValueError

