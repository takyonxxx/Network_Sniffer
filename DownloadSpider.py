import logging
import re
from itertools import chain
from scrapy import signals
from scrapy.crawler import CrawlerProcess
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

control_chars = ''.join(map(chr, chain(range(0, 9), range(11, 32), range(127, 160))))
CONTROL_CHAR_RE = re.compile('[%s]' % re.escape(control_chars))
TEXTRACT_EXTENSIONS = [".pdf", ".doc", ".docx"]
url_list = []


class CustomLinkExtractor(LinkExtractor):
    def __init__(self, *args, **kwargs):
        super(CustomLinkExtractor, self).__init__(*args, **kwargs)
        # Keep the default values in "deny_extensions" *except* for those types we want.
        self.deny_extensions = [ext for ext in self.deny_extensions if ext not in TEXTRACT_EXTENSIONS]


class LinkCheckerSpider(CrawlSpider):
    name = "link_checker"
    start_urls = [
        'https://www.imagescape.com/media/uploads/zinnia/2018/08/20/scrape_me.html'
    ]

    def __init__(self, *args, **kwargs):
        self.rules = (Rule(CustomLinkExtractor(), follow=True, callback="parse_item"),)
        super(LinkCheckerSpider, self).__init__(*args, **kwargs)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(LinkCheckerSpider, cls).from_crawler(crawler, *args, **kwargs)
        # Register the spider_closed handler on spider_closed signal
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self):
        for link in url_list:
            print("Link --> {this_link}".format(this_link=link))

    def parse_item(self, response):
        url_list.append(response.url)
        filename = response.url.split("/")[-1]
        content = response.body
        # response length in bytes
        download_size = len(content) / 1024
        print(filename + " " + str("{0:.1f}".format(download_size)) + " KB")
        # with open(filename, 'wb') as f:
        #    f.write(content)


def print_this_link(link):
    print("Link --> {this_link}".format(this_link=link))


def main():
    # logging.getLogger('scrapy').setLevel(logging.WARNING)
    logging.getLogger('scrapy').propagate = False
    process = CrawlerProcess()
    process.crawl(LinkCheckerSpider)
    process.start()


if __name__ == "__main__":
    main()
