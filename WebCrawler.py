# -*- coding: utf-8 -*-
import time
import requests
import re
from urllib.parse import urlparse
from parsel import Selector

myDict = {}


class PyCrawler(object):
    def __init__(self, starting_url):
        self.starting_url = starting_url
        self.visited = set()

    def get_html(self, url):
        try:
            html = requests.get(url)
        except Exception as e:
            print(e)
            return ""
        return html.content.decode('latin-1')

    def get_links(self, url):
        html = self.get_html(url)
        selector = Selector(html)
        links = selector.xpath('//img/@src').getall()
        # links = re.findall('''<a\s+(?:[^>]*?\s+)?href="([^"]*)"''', html)

        parsed = urlparse(url)
        base = f"{parsed.scheme}://{parsed.netloc}"

        for i, link in enumerate(links):
            if not urlparse(link).netloc:
                link_with_base = base + link
                links[i] = link_with_base

        return set(filter(lambda x: 'mailto' not in x, links))

    def extract_info(self, url):
        html = self.get_html(url)
        meta = re.findall("<meta .*?name=[\"'](.*?)['\"].*?content=[\"'](.*?)['\"].*?>", html)
        return dict(meta)

    def crawl(self, url):
        for link in self.get_links(url):

            if link in self.visited:
                continue

            self.visited.add(link)
            size = is_downloadable(link)
            if not size == 0:
                myDict[link] = size

            self.crawl(link)

    def start(self):
        print("Searching links of : " + self.starting_url)
        self.crawl(self.starting_url)
        sorted_link_list = sorted(myDict.items(), key=lambda x: x[1])
        for link in sorted_link_list:
            print("Downloadable Link -->", link[0], " : ", str("{0:.1f}".format(link[1])), " KB")
            # info = self.extract_info(link)
            # print(info.get('description'))


def is_downloadable(url):
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    content_length = header.get('content-length', None)
    download_size = int(0)
    if content_length:
        download_size = int(str(content_length)) / 1024

    if 'text' in content_type.lower():
        return 0
    if 'html' in content_type.lower():
        return 0

    return download_size


def main():
    start = time.time()
    crawler = PyCrawler("https://github.com/takyonxxx?tab=repositories")
    crawler.start()
    end = time.time()
    print("Time taken in seconds : ", str("{0:.1f}".format(end - start)))


if __name__ == "__main__":
    main()
