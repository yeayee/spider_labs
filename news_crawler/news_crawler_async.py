# -*- coding: UTF-8 -*-

import lzma
import time
import asyncio
import aiohttp
import farmhash
import traceback
import urllib.parse as urlparse

import config
import functions as fn
from mysql_wrapper_async import SanicDB
from url_pool import UrlPool


# 只在Linux平台有效，Windows平台不支持
# import uvloop
# asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())

class NewsCrawlerAsync:
    def __init__(self, name):
        self._workers = 0
        self._workers_max = 32
        self.logger = fn.init_file_logger(name + ".log")
        self.urlpool = UrlPool(name)
        self.loop = asyncio.get_event_loop()
        self.session = aiohttp.ClientSession(loop=self.loop)
        self.db = SanicDB(config.db_host, config.db_name, config.db_username, config.db_password, loop=self.loop)

    async def load_hubs(self):
        sql = "select url from crawler_hub"
        data = await self.db.query(sql)
        self.hub_hosts = set()
        hubs = []
        for d in data:
            host = urlparse.urlparse(d["url"]).netloc
            self.hub_hosts.add(host)
            hubs.append(d["url"])
        self.urlpool.set_hubs(hubs, 600)

    async def save_to_db(self, url, html):
        urlhash = farmhash.hash64(url)
        sql = "select url from crawler_html where urlhash=%s"
        d = await self.db.get(sql, urlhash)
        if d:
            if d['url'] != url:
                msg = 'farmhash collision: %s <=> %s' % (url, d['url'])
                self.logger.error(msg)
            return True
        if isinstance(html, str):
            html = html.encode("utf8")
        html_lzma = lzma.compress(html)
        sql = "insert into crawler_html (urlhash, url, html_lzma) values (%s, %s, %s)"
        good = False
        try:
            await self.db.execute(sql, urlhash, url, html_lzma)
            good = True
        except Exception as e:
            if e.args[0] == 1062:
                # Duplicate entry
                good = True
                pass
            else:
                traceback.print_exc()
                raise e
        return good

    def filter_good(self, urls):
        goodlinks = []
        for url in urls:
            host = urlparse.urlparse(url).netloc
            if host in self.hub_hosts:
                goodlinks.append(url)
        return goodlinks

    async def process(self, url, ishub):
        status, html, redirected_url = await fn.fetch(self.session, url)
        self.urlpool.set_status(url, status)
        if redirected_url != url:
            self.urlpool.set_status(redirected_url, status)
        if status != 200: return
        if ishub:
            newlinks = fn.extract_links_re(redirected_url, html)
            goodlinks = self.filter_good(newlinks)
            print("%s/%s, goodlinks/newlinks - %s" % (len(goodlinks), len(newlinks), url))
            self.urlpool.addmany(goodlinks)
        else:
            await self.save_to_db(redirected_url, html)
        self._workers -= 1

    async def loop_crawl(self):
        await self.load_hubs()
        last_rating_time = time.time()
        counter = 0
        while True:
            tasks = self.urlpool.pop(self._workers_max)
            if not tasks:
                print("no url to crawl, sleep")
                await asyncio.sleep(60)
                continue
            for url, ishub in tasks.items():
                self._workers += 1
                counter += 1
                print(f"crawl: {url}")
                asyncio.ensure_future(self.process(url, ishub))

            gap = time.time() - last_rating_time
            if gap > 5:
                rate = counter / gap
                print('\tloop_crawl() rate:%s, counter: %s, workers: %s' % (round(rate, 2), counter, self._workers))
                last_rating_time = time.time()
                counter = 0
            if self._workers > self._workers_max:
                print('[!] got workers_max, sleep 5 sec to next worker.')
                await asyncio.sleep(5)

    def run(self):
        try:
            self.loop.run_until_complete(self.loop_crawl())
        except KeyboardInterrupt:
            print("stopped by admin!")
            del self.urlpool


if __name__ == '__main__':
    process = NewsCrawlerAsync('news-async')
    process.run()
