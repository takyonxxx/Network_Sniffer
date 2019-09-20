import requests
import urllib.request
import time
from bs4 import BeautifulSoup

url_list = []


def links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    soup.findAll('a')
    url_list = soup.findAll('a')
    for link in url_list:
        print("Link --> {this_link}".format(this_link=link))

    """html = urllib.urlopen(url).read()

    sHtml = str(html)
    for i in range(len(sHtml) - 3):
        if sHtml[i] == '<' and sHtml[i + 1] == 'a' and sHtml[i + 2] == ' ' and sHtml[i + 3] == 'h':
            pos = sHtml[i:].find('</a>')
            print(sHtml[i: i + pos + 4])
            url_list.append(sHtml[i: i + pos + 4])"""


def main():
    links("https://www.imagescape.com/media/uploads/zinnia/2018/08/20/scrape_me.html")


if __name__ == '__main__':
    main()
