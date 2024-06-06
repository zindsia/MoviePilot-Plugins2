import os

import requests
from pyquery import PyQuery as pq

from app.log import logger


class JavLibrary:
    top20_url: str = 'https://www.javlibrary.com/cn/vl_mostwanted.php?page='

    def __init__(self):
        pass

    def crawling_top20(self, page):
        proxies = {
            "http": os.environ.get("HTTP_PROXY"),
            "https": os.environ.get("HTTPS_PROXY")
        }
        res = requests.get(url=f'{self.top20_url}{page}', proxies=proxies, allow_redirects=False)
        doc = pq(res.text)
        page_title = doc('head>title').text()
        codes = []
        if page_title.startswith('最想要的影片'):
            videos = doc('div.video>a').items()
            if videos:
                for video in videos:
                    code = video('a div.id').text()
                    codes.append(code)
        return codes


