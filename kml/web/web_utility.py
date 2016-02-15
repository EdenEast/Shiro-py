__author__ = 'Athena'


from bs4 import BeautifulSoup
import requests
import re


def get_soup_from_url(url):
    html = requests.get(url, auth=('User', 'Pass')).text
    return BeautifulSoup(html, 'html.parser')

def get_pretty_soup_from_url(url):
    html = requests.get(url, auth=('User', 'Pass')).text
    soup = BeautifulSoup(html, 'html.parser')
    return BeautifulSoup(soup.prettify(), 'html.parser')

def remove_html_tag(text):
    print(text)
    cleaner = re.compile('<.*?>')
    return re.sub(cleaner, '', text)