import sys

from crawler import Crawler
from db import RedisClient

POOL_UPPER_THRESHOLD = 1000
class Getter:
    def __init__(self):
        self.redis = RedisClient()
        self.crawler = Crawler()

    def is_over_threshold(self):
        if self.redis.count() >= POOL_UPPER_THRESHOLD:
            return True
        else:
            return False
    
    def run(self):
        print("getter is running")
        if not self.is_over_threshold():
            for callback_label in range(self.crawler.__CrawlFuncCount__):
                callback = self.crawler.__CrawlFunc__[callback_label]
                proxies = self.crawler.get_proxies(callback)
                sys.stdout.flush()
                for proxy in proxies:
                    self.redis.add(proxy)
