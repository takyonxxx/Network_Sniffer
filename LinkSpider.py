import logging
import scrapy
from scrapy import signals
from scrapy.crawler import CrawlerProcess


class LinkCheckerSpider(scrapy.Spider):
    name = 'link_checker'

    def __init__(self, url='https://github.com/takyonxxx?tab=repositories', *args, **kwargs):
        super(LinkCheckerSpider, self).__init__(*args, **kwargs)
        self.start_urls = [url]

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(LinkCheckerSpider, cls).from_crawler(crawler, *args, **kwargs)
        # Register the spider_closed handler on spider_closed signal
        crawler.signals.connect(spider.spider_closed, signals.spider_closed)
        return spider

    def spider_closed(self):
        print('----------')

    def parse(self, response):
        """ Main function that parses downloaded pages """
        # Print what the spider is doing
        print(response.url)
        # Get all the <a> tags
        a_selectors = response.xpath("//a")
        # Loop on each tag
        for selector in a_selectors:
            # Extract the link text
            text = selector.xpath("text()").extract_first()
            # Extract the link href
            link = selector.xpath("@href").extract_first()
            # Create a new Request object
            request = response.follow(link, callback=print_this_link)
            # Return it thanks to a generator
            yield request


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
