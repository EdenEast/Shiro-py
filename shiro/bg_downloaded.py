from shiro.library import Library
from queue import Queue
import threading
from PyQt4 import QtCore


class MangaUpdateWorker(QtCore.QThread):
    data_updated = QtCore.pyqtSignal(object)

    def __init__(self, parent):
        super(MangaUpdateWorker, self).__init__()
        self._parent = parent
        self.q = Queue()
        self.thread().daemon = True
        self._abort = False

    def abort(self):
        self._abort = True

    def push(self, title):
        self.q.put(title)

    def run(self):
        while not self.q.empty() and not self._abort:
            title = self.q.get()
            self.update_manga(title)
            self.q.task_done()
        self.data_updated.emit('\n{} Update Completed {}'.format('-' * 21, '-' * 21))

    def update_manga(self, title):
        factor = 60 - (len(title) + 2)
        self.data_updated.emit('{}: {}\n'.format(title, '-' * factor))
        chapters = Library.update_manga_by_title(title)
        if len(chapters) > 0:
            for chapter in chapters:
                self.data_updated.emit('     {}\n'.format(chapter.title))
        # else:
            # self.data_updated.emit('\n')
            # self.data_updated.emit('    Up To Date\n\n')


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
        while not self.q.empty() and not self._abort:
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

