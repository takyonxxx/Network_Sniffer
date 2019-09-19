from bs4 import BeautifulSoup
import requests
from urllib.request import urlopen


def links(url):
    html = str(urlopen(url).read())

    for i in range(len(html) - 3):
        if html[i] == '<' and html[i + 1] == 'a' and html[i + 2] == ' ' and html[i + 3] == 'h':
            pos = html[i:].find('</a>')
            print(html[i: i + pos + 4])


def main():
    links("https://github.com/takyonxxx?tab=repositories")


if __name__ == '__main__':
    main()
