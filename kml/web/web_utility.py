from bs4 import BeautifulSoup
import requests
import re
import shutil


def get_soup_from_url(url):
    html = requests.get(url, auth=('User', 'Pass')).text
    return BeautifulSoup(html, 'html.parser'), html


def get_pretty_soup_from_url(url):
    html = requests.get(url, auth=('User', 'Pass')).text
    soup = BeautifulSoup(html, 'html.parser')
    return BeautifulSoup(soup.prettify(), 'html.parser')


def remove_html_tag(text):
    print(text)
    cleaner = re.compile('<.*?>')
    return re.sub(cleaner, '', text)


def download_image(file, src):
    r = requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'})
    if r.status_code == 200:
        with open(file, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)
    else:
        print('[ERROR download_image] error code {}'.format(r.status_code))
