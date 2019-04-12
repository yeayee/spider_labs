# -*- coding: UTF-8 -*-

import time
import pickle
import leveldb
import urllib.parse as urlparse


class UrlPool:
    """
        URL Pool for crawler to manage URLs
        不重抓，不漏抓
    """

    def __init__(self, pool_name):
        self.name = pool_name

        # self.db 是一个UrlDB的示例，用来永久存储url的永久状态
        self.db = UrlDB(pool_name)

        # self.pool 是用来存放url的，它是一个字典（dict）结构，key是url的host，value是一个用来存储这个host的所有url的集合(set)。
        self.pool = {}  # host: set([urls]), 记录待下载的URL

        # self.pending 用来管理正在下载的url状态。它是一个字典结构，key是url，value是它被pop的时间戳。
        # 当一个url被pop()时，就是它被下载的开始。当该url被set_status()时，就是下载结束的时刻。
        # 如果一个url被add() 入pool时，发现它已经被pended的时间超过pending_threshold时，就可以再次入库等待被下载。
        # 否则，暂不入池。
        self.pending = {}  # url: pended_time, 记录已被pend但还未被更新状态（正在下载）的URL

        # self.failue 是一个字典，key是url，value是识别的次数，超过failure_threshold就会被永久记录为失败，不再尝试下载。
        self.failure = {}  # url: times, 记录失败的URL的次数
        self.failure_threshold = 3
        self.pending_threshold = 60  # pending的最大时间，过期要重新下载
        self.in_mem_count = 0
        self.max_hosts = ["", 0]  # [host:url_count] 目前pool中url最多的host以及其url数量

        # hub_pool 是一个用来存储hub页面的字典，key是hub url，value是上次刷新该hub页面的时间
        self.hub_pool = {}  # {url: last_query_time}
        self.hub_refresh_span = 0
        self.load_cache()

    def load_cache(self):
        """load_cache() 在 init()中调用，创建pool的时候，尝试去加载上次退出时缓存的URL pool"""
        path = self.name + ".pkl"
        try:
            with open(path, "rb") as f:
                self.pool = pickle.load(f)
            cc = [len(v) for k, v in self.pool]
            print(f"saved pool loaded! urls:{sum(cc)}")
        except:
            pass

    def set_hubs(self, urls, hub_refresh_span):
        """
            hub网页就是像百度新闻那样的页面，整个页面都是新闻的标题和链接，是我们真正需要的新闻的聚合页面，并且这样的页面会不断更新，把最新的新闻聚合到这样的页面，我们称它们为hub页面，其URL就是hub url。
            在新闻爬虫中添加大量的这样的url，有助于爬虫及时发现并抓取最新的新闻
        """
        self.hub_refresh_span = hub_refresh_span
        self.hub_pool = {}
        for url in urls:
            self.hub_pool[url] = 0

    def add(self, url, always=False):
        """
            把url放入网址池时，先检查内存中的self.pending是否存在该url，即是否正在下载该url。如果正在下载就不入池；如果正下载或已经超时，就进行到下一步；
            接着检查该url是否已经在leveldb中存在，存在就表明之前已经成功下载或彻底失败，不再下载了也不入池。如果没有则进行到下一步；
            最后通过push_to_pool() 把url放入self.pool中。存放的规则是，按照url的host进行分类，相同host的url放到一起，在取出时每个host取一个url，尽量保证每次取出的一批url都是指向不同的服务器的，
            这样做的目的也是为了尽量减少对抓取目标服务器的请求压力。力争做一个服务器友好的爬虫！
        """
        if always:
            return self.push_to_pool(url)

        pended_time = self.pending.get(url, 0)
        if time.time() - pended_time < self.pending_threshold:  # 正在下载中的URL
            print("being downloading:", url)
            return
        if self.db.has(url):  # 永久存储数据库已经有了，说明已经爬过
            return
        if pended_time:  # 已经超时的URL，需要重新放入池中，等待下次尝试
            self.pending.pop(url)
        return self.push_to_pool(url)

    def push_to_pool(self, url):
        host = urlparse.urlparse(url).netloc
        if not host or "." not in host:
            print(f"try to push_to_pool with bad url:{url}, len of url: {len(url)}")
            return False
        if host in self.pool:
            if url in self.pool[host]:
                return True
            self.pool[host].add(url)
            if len(self.pool[host]) > self.max_hosts[1]:
                self.max_hosts[1] = len(self.pool[host])
                self.max_hosts[0] = host
        else:
            self.pool[host] = set([url])
        self.in_mem_count += 1
        return True

    def pop(self, count, hubpercent=50):
        """
            爬虫通过该方法，从网址池中获取一批url去下载。取出url分两步：
            第一步，先从self.hub_pool中获得，方法是遍历hub_pool，检查每个hub-url距上次被pop的时间间隔是否超过hub页面刷新间隔(self.hub_refresh_span)，来决定hub-url是否应该被pop。
            第二步，从self.pool中获取。前面push_to_pool中，介绍了pop的原则，就是每次取出的一批url都是指向不同服务器的，有了self.pool的特殊数据结构，安装这个原则获取url就简单了，按host（self.pool的key）遍历self.pool即可。
        """
        print(f"\b\tmax of host:{self.max_hosts}")

        # 取出的url有两种类型：hub, 普通
        url_attr_url = 0  # 普通
        url_attr_hub = 1  # hub
        # 1. 首先取出hub，保证获取hub里的最新url
        hubs = {}
        hub_count = count * hubpercent // 100
        for hub in self.hub_pool:
            span = time.time() - self.hub_pool[hub]
            if span < self.hub_refresh_span:
                continue
            hubs[hub] = url_attr_hub  # Hub URL
            self.hub_pool[hub] = time.time()  # 更新hub的访问时间
            if len(hubs) >= hub_count:
                break

        # 2. 取出普通url，如果某个host有太多url，则每次可以获取几个它的url
        if self.max_hosts[1] * 10 > self.in_mem_count:
            delta = 3
            print(f"\t set delta：{delta}, max of host:{self.max_hosts}")
        else:
            delta = 1
        left_count = count - len(hubs)
        urls = {}
        for host in self.pool:
            if not self.pool[host]:  # empty host
                continue
            if self.max_hosts[0] == host:
                while delta > 0:
                    url = self.pool[host].pop()
                    self.max_hosts[1] -= 1
                    if not self.pool[host]:
                        break
                    delta -= 1
            else:
                url = self.pool[host].pop()
            urls[url] = url_attr_url  # 普通
            self.pending[url] = time.time()  # 记录URL开始的访问时间
            if len(urls) >= left_count:
                break
        self.in_mem_count -= len(urls)
        print(f"To pop:{count}, hubs: {len(hubs)}, urls:{len(urls)}, hosts:{len(self.pool)}")
        urls.update(hubs)
        return urls

    def addmany(self, urls, always=False):
        if isinstance(urls, str):
            print(f"urls is a str !!! {urls}")
            self.add(urls)
        else:
            for url in urls:
                self.add(url, always)

    def size(self):
        return self.in_mem_count

    def empty(self):
        return self.in_mem_count == 0

    def set_status(self, url, status_code):
        if url in self.pending:
            self.pending.pop(url)
        if status_code == 200:
            self.db.set_success(url)
            return
        if status_code == 404:
            self.db.set_failure(url)
            return
        if url in self.failure:
            self.failure[url] += 1
            if self.failure[url] > self.failure_threshold:
                self.db.set_failure(url)
                self.failure.pop(url)
            else:
                self.add(url)
        else:
            self.failure[url] = 1

    def __del__(self):
        """dump_cache() 在 del() 中调用，也就是在网址池销毁前（比如爬虫意外退出），把内存中的URL pool缓存到硬盘。"""
        path = self.name + ".pkl"
        try:
            with open(path, "wb") as f:
                pickle.dump(self.pool, f)
            print(f"self.pool saved!")
        except:
            pass


class UrlDB:
    """use leveldb to store URLs what have been done(succeed or failed"""
    status_failure = b"0"
    status_success = b"1"

    def __init__(self, db_name):
        self.name = db_name + ".urldb"
        self.db = leveldb.LevelDB(self.name)

    def load_from_db(self, status):
        urls = []
        for url, _status in self.db.RangeIter():
            if status == _status:
                urls.append(url)
        return urls

    def set_success(self, url):
        if isinstance(url, str):
            url = url.encode("utf8")
        try:
            self.db.Put(url, self.status_success)
            s = True
        except:
            s = False
        return s

    def set_failure(self, url):
        if isinstance(url, str):
            url = url.encode("utf8")
        try:
            self.db.Put(url, self.status_failure)
            s = True
        except:
            s = False
        return s

    def has(self, url):
        if isinstance(url, str):
            url = url.encode("utf8")
        try:
            attr = self.db.Get(url)
            return attr
        except:
            pass
        return False
