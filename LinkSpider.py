from bs4 import BeautifulSoup
from urllib.request import Request, urlopen, urlretrieve
from urllib.error import URLError, HTTPError

url_list = []


def get_size(link):
    try:
        return int(urlopen(link).headers.get("Content-Length"))
    except:
        return 0


def links(url):
    req = Request(url)
    try:

        response = urlopen(req)
        soup = BeautifulSoup(response.read(), "html.parser")
        soup.findAll('a')
        url_list = soup.findAll('a')
        for link in url_list:
            print("Link --> {this_link}".format(this_link=link))
    except HTTPError as e:
        print('The server couldn\'t fulfill the request.')
        print('Error code: ', e.code)
    except URLError as e:
        print('We failed to reach a server.')
        print('Reason: ', e.reason)


def main():
    links("http://www.example.com/")


if __name__ == '__main__':
    main()
