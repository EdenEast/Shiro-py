from kml.library import Library
from queue import Queue
import threading

running = True
running_lock = threading.Lock()
target_list = []
target_list_lock = threading.Lock()
message_lock = threading.Lock()
thread = None
q = Queue()
stop_by_force = False


def start():
    global thread
    thread = threading.Thread(target=run)
    thread.daemon = True
    thread.start()


def push(target, args):
    global q
    q.put((target, args))


def run():
    global q
    global thread
    while not q.empty() and not stop_by_force:
        target, args = q.get()
        target(args)
        q.task_done()
    clear_queue()


def force_stop():
    global stop_by_force
    stop_by_force = True


def is_running():
    global q
    return not q.empty()


def clear_queue():
    global q
    with q.mutex:
        q.queue.clear()
    q.join()


def download_manga(manga, status_bar):
    for chapter in manga.chapter_list:
        push(download_chapter, (chapter, status_bar))


def download_chapter(args):
    global message_lock
    chapter = args[0]
    status_bar = args[1]

    with message_lock:
        status_bar.showMessage('Downloading {}: {}'.format(chapter.parent.title, chapter.title))
    chapter.parent.site.download_chapter_threaded(chapter)
    cmd = cmd = "UPDATE chapter SET downloaded=1 WHERE manga_id={} AND title='{}'".format(
        chapter.parent.hash, chapter.title)
    Library.db.cursor().execute(cmd)
    Library.db.commit()
