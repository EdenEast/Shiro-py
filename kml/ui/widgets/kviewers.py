from PyQt4.QtGui import *
from PyQt4.QtWebKit import *
from PyQt4 import QtCore
from PyQt4.QtGui import QColor
from kml.library import Library
from PIL import Image, ImageQt
import os
import zipfile


class KPageViewer(QScrollArea):
    def __init__(self, parent, chapter=None):
        super(KPageViewer, self).__init__()
        # This is the page label that will have the page image
        self._parent = parent
        self.label = QLabel()
        self.chapter = chapter
        self.current_page = 0
        self.pages = []
        self.fit_type = 0
        self.rotate_angle = 0

        if self.chapter:
            self.load_chapter(chapter)

        self.drag_mouse = False
        self.drag_position = {'x': 0, 'y': 0}
        self.setCursor(QtCore.Qt.OpenHandCursor)
        self.setWidget(self.label)
        self.setAlignment(QtCore.Qt.AlignCenter)
        self.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        color = QColor('#262626')
        style = "QWidget { background-color: %s }" % color.name()
        self.setStyleSheet(style)

    def reset_scroll_position(self):
        self.verticalScrollBar().setValue(0)

    def change_background_color(self, color):
        style = "QWidget { background-color: %s }" % color.name()
        self.setStyleSheet(style)

    def mousePressEvent(self, *args, **kwargs):
        self.drag_mouse = True
        self.drag_position['x'] = args[0].x()
        self.drag_position['y'] = args[0].y()
        self.setCursor(QtCore.Qt.ClosedHandCursor)
        super(KPageViewer, self).mousePressEvent(*args, **kwargs)

    def mouseMoveEvent(self, *args, **kwargs):
        if self.drag_mouse:
            scroll_position = {
                'x' : self.horizontalScrollBar().sliderPosition(),
                'y' : self.verticalScrollBar().sliderPosition()
            }
            new_x = scroll_position['x'] + self.drag_position['x'] - args[0].x()
            new_y = scroll_position['y'] + self.drag_position['y'] - args[0].y()

            self.horizontalScrollBar().setSliderPosition(new_x)
            self.verticalScrollBar().setSliderPosition(new_y)

            self.drag_position['x'] = args[0].x()
            self.drag_position['y'] = args[0].y()
        super(KPageViewer, self).mouseMoveEvent(*args, **kwargs)

    def mouseReleaseEvent(self, *args, **kwargs):
        self.drag_mouse = False
        self.setCursor(QtCore.Qt.OpenHandCursor)

    def load_chapter(self, chapter):
        self.chapter = chapter
        self.current_page = 0
        file_name = os.path.join(Library.directory, chapter.parent.title, chapter.get_file_name())
        with zipfile.ZipFile(file_name) as archive:
            self.pages.clear()
            for entry in archive.infolist():
                with archive.open(entry) as file:
                    if '.ini' not in file.name:
                        self.pages.append(Image.open(file))
        self.set_content(self.get_current_page())

    def page_down(self):
        value = self.verticalScrollBar().value()
        maximum = self.verticalScrollBar().maximum()

        if value == maximum:
            self.next_page()
            return

        page_step = self.verticalScrollBar().pageStep()
        page_step -= page_step * 0.15
        self.verticalScrollBar().setValue(value + page_step)

    def page_up(self):
        value = self.verticalScrollBar().value()
        minimum = self.verticalScrollBar().minimum()

        if value == minimum:
            self.prev_page()
            return

        page_step = self.verticalScrollBar().pageStep()
        page_step -= page_step * 0.15
        self.verticalScrollBar().setValue(value - page_step)

    def next_page(self):
        if self.current_page < len(self.pages) - 1:
            self.current_page += 1
            self.set_content(self.get_current_page())
        else:
            Library.db.cursor().execute('UPDATE chapter SET completed=1 WHERE manga_id={} AND title=\'{}\''
                                        .format(self.chapter.parent.hash, self.chapter.title))
            Library.db.commit()
            self.next_chapter()

    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.set_content(self.get_current_page())
            self.verticalScrollBar().setValue(self.verticalScrollBar().maximum())
        else:
            self.prev_chapter()

    def next_chapter(self):
        chapter = self.chapter.parent.next_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.current_page = 0
            self.load_chapter(chapter)

    def prev_chapter(self):
        chapter = self.chapter.parent.prev_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.load_chapter(chapter)
            self.current_page = len(self.pages) - 1
            self.set_content(self.get_current_page())

    def first_page(self):
        self.current_page = 0
        self.set_content(self.get_current_page())

    def last_page(self):
        self.current_page = len(self.pages) - 1
        self.set_content(self.get_current_page())

    def rotate_left(self):
        self.rotate_angle = (self.rotate_angle - 90) % 360
        self.set_content(self.get_current_page())

    def rotate_right(self):
        self.rotate_angle = (self.rotate_angle + 90) % 360
        self.set_content(self.get_current_page())

    def original_fit(self):
        self.fit_type = 0
        self.set_content(self.get_current_page())

    def vertical_fit(self):
        self.fit_type = 1
        self.set_content(self.get_current_page())

    def horizontal_fit(self):
        self.fit_type = 2
        self.set_content(self.get_current_page())

    def best_fit(self):
        self.fit_type = 3
        self.set_content(self.get_current_page())

    def get_current_page(self):
        image_qt = ImageQt.ImageQt(self.pages[self.current_page])
        pix_map = QPixmap.fromImage(image_qt.copy())
        pix_map = self.rotate_page(pix_map)
        pix_map = self.resize_page(pix_map)
        return pix_map

    def set_content(self, content):
        if content:
            self.label.setPixmap(content)
            self.label.resize(content.size())
            self.reset_scroll_position()
            self.update_title()

    def reload(self):
        self.set_content(self.get_current_page())

    def update_title(self):
        title = '{}: {} ( {} | {} )'.format(self.chapter.parent.title, self.chapter.title,
                                            self.current_page + 1, len(self.pages))
        self._parent.setWindowTitle(title)

    def resize_page(self, pix_map):
        if self.fit_type == 1:
            pix_map = pix_map.scaledToHeight(
                self.size().height() - 2,
                QtCore.Qt.SmoothTransformation)
        elif self.fit_type == 2:
            pix_map = pix_map.scaledToWidth(
                self.size().width(),
                QtCore.Qt.SmoothTransformation)
        elif self.fit_type == 3:
            ratio = pix_map.width() / pix_map.height()
            if ratio < 1:
                pix_map = pix_map.scaledToWidth(
                    self.size().width() * 0.8,
                    QtCore.Qt.SmoothTransformation)
            else:
                pix_map = pix_map.scaledToHeight(
                    self.size().height() * 0.95,
                    QtCore.Qt.SmoothTransformation)
        return pix_map

    def rotate_page(self, pix_map):
        if self.rotate_angle != 0:
            transform = QTransform().rotate(self.rotate_angle)
            pix_map = QPixmap(pix_map.transformed(transform))
        return pix_map


class KWebViewer(QWebView):
    def __init__(self, parent, chapter=None):
        super(KWebViewer, self).__init__()
        self._parent = parent
        self.chapter = chapter
        self.page_list = []
        self.beginning_html = """<html>
    <head>
        <style>
            img{
                border: 0;
                margin: 0;
                max-width: 99%;
            }
            p.imagePage{
                margin: 0 0 10px;
                display: block;
                text-align: center;
            }
        </style>
    </head>
    <body bgcolor="#262626">\n"""
        self.ending_html = """    </body>
</html>"""

        if chapter:
            self.load_chapter(self.chapter)

    def load_chapter(self, chapter):
        link_list = chapter.parent.site.get_all_pages_from_chapter(chapter.url)
        self.page_list.clear()
        for link in link_list:
            self.add_page(link)
        self.reload_page()

    def add_page(self, page):
        self.page_list.append(page)

    def reload_page(self):
        html = self.beginning_html
        for page in self.page_list:
            html += '\t\t<p class="imagePage"><img src="{}"></p>\n'.format(page)
        html += self.ending_html
        self.setHtml(html)
        self.update_window_title()

    def update_window_title(self):
        text = '{}: {}'.format(self.chapter.parent.title, self.chapter.title)
        self._parent.setWindowTitle(text)

    def calculate_page_step(self):
        # http://stackoverflow.com/questions/22035363/formula-for-content-step-of-scrollbar
        content_height = self.page().mainFrame().contentsSize().height()
        viewport_height = self.page().viewportSize().height()

        if content_height == 0:
            return 0

        # calculating the thumb height
        viewable_ratio = viewport_height / content_height
        scroll_bar_area = viewport_height - 50
        thumb_height = scroll_bar_area * viewable_ratio

        scroll_tracking_space = content_height - viewport_height
        scroll_thumbnail_space = viewport_height - thumb_height
        step = scroll_tracking_space / scroll_thumbnail_space
        return step

    def page_down(self):
        value = self.vertical_scroll_bar()
        if value == self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical):
            Library.db.cursor().execute('UPDATE chapter SET completed=1 WHERE manga_id={} AND title=\'{}\''
                                        .format(self.chapter.parent.hash, self.chapter.title))
            Library.db.commit()
            self.next_chapter()
        page_step = self.calculate_page_step()
        self.set_vertical_scroll_bar(value + page_step)

    def page_up(self):
        value = self.vertical_scroll_bar()
        if value == self.page().mainFrame().scrollBarMinimum(QtCore.Qt.Vertical):
            self.prev_chapter()
        page_step = self.calculate_page_step()
        self.set_vertical_scroll_bar(value - page_step)

    def next_page(self):
        self.next_chapter()

    def prev_page(self):
        self.prev_chapter()

    def next_chapter(self):
        chapter = self.chapter.parent.next_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.load_chapter(chapter)

    def prev_chapter(self):
        chapter = self.chapter.parent.prev_chapter(self.chapter)
        if chapter != self.chapter:
            self.chapter = chapter
            self.load_chapter(chapter)

    def first_page(self):
        self.set_vertical_scroll_bar(self.page().mainFrame().scrollBarMinimum(QtCore.Qt.Vertical))

    def last_page(self):
        self.set_vertical_scroll_bar(self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical))

    def vertical_scroll_bar(self):
        return self.page().mainFrame().scrollBarValue(QtCore.Qt.Vertical)

    def set_vertical_scroll_bar(self, value):
        self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, value)

    def set_chapter(self, chapter):
        self.chapter = chapter
        self.load_chapter(chapter)

    def rotate_left(self):
        pass

    def rotate_right(self):
        pass

    def original_fit(self):
        pass

    def vertical_fit(self):
        pass

    def horizontal_fit(self):
        pass

    def best_fit(self):
        pass


# class KWebViewerOld(QWebView):
#     def __init__(self, parent, chapter):
#         super(KWebViewer, self).__init__()
#         self.url_image_list = []
#         self.current_url_index = 0
#         self.chapter = None
#         html = '<body bgcolor="Red"></body>'
#         self.beginning_html = """<html>
#     <head>
#         <style>
#             img{
#                 border: 0;
#                 margin: 0;
#                 max-width: 99%;
#             }
#             p.imagePage{
#                 margin: 0 0 10px;
#                 display: block;
#                 text-align: center;
#             }
#         </style>
#     </head>
#     <body bgcolor="#262626">\n"""
#         self.ending_html = """    </body>
# </html>"""
#         self.setHtml(html)
#
#     def load_url(self, url):
#         img_attr = '<img src="{}">'.format(url)
#         html = '<body bgcolor="Red">{}</body>'.format(img_attr)
#         self.setHtml(html)
#
#     def load_entire_chapter(self):
#         html = self.beginning_html
#         for page in self.url_image_list:
#             html += '\t\t<p class="imagePage"><img src="{}"></p>\n'.format(page)
#         html += self.ending_html
#         self.setHtml(html)
#
#     def add_image_url(self, url):
#         self.url_image_list.append(url)
#
#     def remove_image_url(self, url):
#         self.url_image_list.remove(url)
#
#     def reload_page(self):
#         self.load_url(self.url_image_list[self.current_url_index])
#
#     def reload_chapter(self):
#         self.load_entire_chapter()
#
#     def next_url(self):
#         if self.current_url_index <= len(self.url_image_list):
#             self.current_url_index += 1
#
#     def prev_url(self):
#         if self.current_url_index > 0:
#             self.current_url_index -= 1
#
#     def is_at_bottom(self):
#         return self.get_vertical_scrollbar_value() == self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical)
#
#     def is_at_top(self):
#         return self.get_vertical_scrollbar_value() == self.page().mainFrame().scrollBarMinimum(QtCore.Qt.Vertical)
#
#     def calculate_page_step(self):
#         # http://stackoverflow.com/questions/22035363/formula-for-content-step-of-scrollbar
#         content_height = self.page().mainFrame().contentsSize().height()
#         viewport_height = self.page().viewportSize().height()
#
#         # calculating the thumb height
#         viewable_ratio = viewport_height / content_height
#         scroll_bar_area = viewport_height - 50
#         thumb_height = scroll_bar_area * viewable_ratio
#
#         scroll_tracking_space = content_height - viewport_height
#         scroll_thumbnail_space = viewport_height - thumb_height
#         step = scroll_tracking_space / scroll_thumbnail_space
#         return step
#
#     def page_down(self):
#         value = self.get_vertical_scrollbar_value()
#
#         if value == self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical):
#             return False
#
#         page_step = self.calculate_page_step() * 0.15
#         self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, value + page_step)
#         return True
#
#     def page_up(self):
#         value = self.get_vertical_scrollbar_value()
#         if value == self.page().mainFrame().scrollBarMinimum(QtCore.Qt.Vertical):
#             return False
#
#         page_step = self.calculate_page_step() * 0.15
#         self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, value + page_step)
#         return True
#
#     def next_page(self):
#         if not self.page_down():
#             self.next_chapter()
#             return False
#         return True
#
#     def prev_page(self):
#         if not self.page_up():
#             self.prev_chapter()
#             return False
#         return True
#
#     def next_chapter(self):
#         chapter = self.chapter.parent.next_chapter(self.chapter)
#         if chapter != self.chapter:
#             self.chapter = chapter
#             self.load_entire_chapter(chapter)
#
#     def prev_chapter(self):
#         chapter = self.manga.prev_chapter(self.chapter)
#         if chapter != self.chapter:
#             self.chapter = chapter
#             self.load_entire_chapter(chapter)
#
#     def first_page(self):
#         self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, 0)
#
#     def last_page(self):
#         self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, self.page().mainFrame().scrollBarMaximum(QtCore.Qt.Vertical))
#
#     def get_vertical_scrollbar_value(self):
#         return self.page().mainFrame().scrollBarValue(QtCore.Qt.Vertical)
#
#     def set_vertical_scrollbar(self, value):
#         self.page().mainFrame().setScrollBarValue(QtCore.Qt.Vertical, value)
#
#     def set_chapter(self, chapter):
#         self.chapter = chapter
#
#     def rotate_left(self):
#         pass
#
#     def rotate_right(self):
#         pass
#
#     def original_fit(self):
#         pass
#
#     def vertical_fit(self):
#         pass
#
#     def horizontal_fit(self):
#         pass
#
#     def best_fit(self):
#         pass




