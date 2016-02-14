__author__ = 'Athena'


from PyQt4.QtWebKit import QWebView

class KWebViewer(QWebView):
    def __init__(self):
        super(QWebView, self).__init__()
        self.url_image_list = []
        self.current_url_index = 0
        self.image_height = 0
        self.background_color = 'Grey'
        html = '<body bgcolor="%s"></body>' % self.background_color
        self.setHtml(html)

    def load_url(self, url):
        img_atr = '<img src="%s" alt="%s">' % (url, self.image_height)
        html = '<body bgcolor="%s"><center>%s</center></body>' % (self.background_color, img_atr)
        self.setHtml(html)

    def add_image_url(self, url):
        self.url_image_list.append(url)

    def remove_image_url(self, url):
        self.url_image_list.remove(url)

    def reload_page(self):
        self.load_url(self.url_image_list[self.current_url_index])

    def next_url(self):
        if self.current_url_index <= len(self.url_image_list):
            self.current_url_index += 1

    def previous_url(self):
        if self.current_url_index > 0:
            self.current_url_index -= 1

    def set_zoom_level(self, factor):
        self.setZoomFactor(factor)

    def clear_url_list(self):
        self.url_image_list = []