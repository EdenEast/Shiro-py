from io import BytesIO
import threading
import time
import zipfile

running = True
running_lock = threading.Lock()
target_list = []
target_list_lock = threading.Lock()
thread = None


def initialize():
    global thread
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


def run():
    global running
    global target_list
    global target_list_lock
    while running:
        while len(target_list) == 0:
            time.sleep(0.2)
        with target_list_lock:
            target, args = target_list.pop(0)
        target(args)


def push(target, args):
    global target_list
    global target_list_lock
    with target_list_lock:
        target_list.append((target, args))


def join():
    global running
    global running_lock
    global target_list
    while len(target_list) > 0:
        time.sleep(0.2)
    with running_lock:
        running = False


def force_stop():
    global running
    running = False


def save_to_archive(args):
    images = args[0]
    file_path = args[1]
    info_string = args[2]

    buffer = BytesIO()
    zip_file = zipfile.ZipFile(buffer, 'w')
    images.sort(key=lambda tup: tup[0])
    for image in images:
        zip_file.writestr(image[0], image[1])
    zip_file.writestr('info.ini', info_string)
    zip_file.close()
    with open(file_path, 'wb') as archive:
        archive.write(buffer.getvalue())
    buffer.close()


# class BGFileIO(object):
#     running = True
#     running_lock = threading.Lock()
#     list = []
#     list_lock = threading.Lock()
#     thread = None
#
#     @staticmethod
#     def initialize():
#         BGFileIO.thread = threading.Thread(target=BGFileIO.run)
#         BGFileIO.thread.daemon = True
#         BGFileIO.thread.start()
#
#     @staticmethod
#     def push(target, args):
#         with BGFileIO.list_lock:
#             BGFileIO.list.append((target, args))
#
#     @staticmethod
#     def join():
#         while len(BGFileIO.list) > 0:
#             time.sleep(0.2)
#         with BGFileIO.running_lock:
#             BGFileIO.running = False
#
#     @staticmethod
#     def run():
#         while BGFileIO.running:
#             while len(BGFileIO.list) == 0:
#                 time.sleep(0.2)
#             with BGFileIO.list_lock:
#                 target, args = BGFileIO.list.pop(0)
#             target(args)
#
#     @staticmethod
#     def force_stop():
#         with BGFileIO.running_lock:
#             BGFileIO.running = False
#
