import json
import re
from utils import downloader
from pyquery import PyQuery

class ProxyMetaclass(type):
    def __new__(cls, name, bases, attrs):
        count = 0
        attrs["__CrawlFunc__"] = []
        for k, v in attrs.items():
            if "crawl_" in k:
                attrs["__CrawlFunc__"].append(k)
                count += 1
        attrs["__CrawlFuncCount__"] = count
        return type.__new__(cls, name, bases, attrs)

class Crawler(object, metaclass=ProxyMetaclass):
    def get_proxies(self, callback):
        proxies = []
        for proxy in eval("self.{}()".format(callback)):
            print(f"get {proxy}")
            proxies.append(proxy)
        return proxies
    
    def crawl_daili66(self, page_count=4):
        start_url = "http://www.66ip.cn/{}.html"
        urls = [start_url.format(i) for i in range(1, page_count+1)]
        for url in urls:
            print(f"crawling {url}")
            html = downloader(url)
            if html:
                doc = PyQuery(html)
                trs = doc('.containerbox table tr:gt(0)').items()
                for tr in trs:
                    ip = tr.find("td:nth-child(1)").text()
                    port = tr.find("td:nth-child(2)").text()
                    yield ":".join([ip, port])
    
    def crawl_ip3366(self):
        for i in range(1, 4):
            start_url = 'http://www.ip3366.net/?stype=1&page={}'.format(i)
            html = downloader(start_url)
            if html:
                find_tr = re.compile('<tr>(.*?)</tr>', re.S)
                trs = find_tr.findall(html)
                for s in range(1, len(trs)):
                    find_ip = re.compile('<td>(\d+\.\d+\.\d+\.\d+)</td>')
                    re_ip_address = find_ip.findall(trs[s])
                    find_port = re.compile('<td>(\d+)</td>')
                    re_port = find_port.findall(trs[s])
                    for address,port in zip(re_ip_address, re_port):
                        address_port = address+':'+port
                        yield address_port.replace(' ','')