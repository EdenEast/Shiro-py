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


def save_manga_info(args):
    text = args[0]
    file_path = args[1]

    with open(file_path, 'w') as info_file:
        info_file.write(text)
