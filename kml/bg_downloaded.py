from kml.library import Library
from queue import Queue
import threading
from PyQt4 import QtCore

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


class ChapterDownloadWorker(QtCore.QThread):
    data_downloaded = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super(ChapterDownloadWorker, self).__init__()
        self._parent = parent
        self.q = Queue()
        self._abort = False

    def abort(self):
        self._abort = True

    def push(self, chapter):
        self.q.put(chapter)

    def run(self):
        while self.q.not_empty and not self._abort:
            chapter = self.q.get()
            self.download_chapter(chapter)
            self.q.task_done()
        if self._abort:
            if self.q.not_empty:
                with self.q.mutex:
                    title = self.q.queue[0].parent.title
                    self.q.queue.clear()
            self.data_downloaded.emit('Download Aborted for: {}'.format(title))
        else:
            self.data_downloaded.emit('')

    def download_chapter(self, chapter):
        site = chapter.parent.site
        self.data_downloaded.emit('Downloading: {}'.format(chapter.title))
        site.download_chapter_threaded(chapter)
        self.data_downloaded.emit('Update Library for: {}'.format(chapter.title))
        self.update_chapter_library(chapter)
        self.data_downloaded.emit('Completed: {}'.format(chapter.title))
        self._parent.update_chapter_table()


    def update_chapter_library(self, chapter):
        query = "UPDATE chapter SET downloaded=1 WHERE manga_id={} AND title='{}'"\
            .format(chapter.parent.hash, chapter.title)
        Library.db.cursor().execute(query)
        Library.db.commit()

