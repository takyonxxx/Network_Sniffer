import requests
import aiohttp
import asyncio
from parsel import Selector
import time

start = time.time()
all_images = {}  # website links as "keys" and images link as "values"


async def fetch(session, url):
    try:
        async with session.get(url) as response:
            return await response.text()
    except Exception as exp:
        return '<html> <html>'  # empty html for invalid uri case


async def search(urls):
    tasks = []
    async with aiohttp.ClientSession() as session:
        for url in urls:
            tasks.append(fetch(session, url))
        htmls = await asyncio.gather(*tasks)
        for index, html in enumerate(htmls):
            selector = Selector(html)
            image_links = selector.xpath('//img/@src').getall()
            for link in image_links:
                if str(link):
                    print("Link --> {this_link}".format(this_link=link))


def main():
    response = requests.get('https://github.com/takyonxxx?tab=repositories')
    selector = Selector(response.text)
    href_links = selector.xpath('//a/@href').getall()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(search(href_links))

    print("All done !")
    end = time.time()
    print("Time taken in seconds : ", (end - start))


if __name__ == '__main__':
    main()
