import asyncio
import aiohttp
import time
import sys
try:
    from aiohttp import ClientError
except:
    from aiohttp import ClientProxyConnectionError as ClientProxyConnectionError
from db import RedisClient
from setting import *

class Tester:
    def __init__(self):
        self.redis = RedisClient()
    
    async def test_single_proxy(self, proxy):
        conn = aiohttp.TCPConnector(verify_ssl=False)
        async with aiohttp.ClientSession(connector=conn) as session:
            try:
                if isinstance(proxy, bytes):
                    proxy = proxy.decode("utf8")
                real_proxy = "http://"+proxy
                print(f"testing {proxy}")
                async with session.get(TEST_URL, proxy=real_proxy, timeout=15, allow_redirects=False) as response:
                    if response.status in VALID_STATUS_CODES:
                        self.redis.max(proxy)
                        print(f"{proxy} can use.")
                    else:
                        self.redis.decrease(proxy)
                        print(f"request is invalid {response.status} by proxy ip {proxy}")
            except (ClientError, aiohttp.client_exceptions.ClientConnectionError, asyncio.TimeoutError, AttributeError):
                self.redis.decrease(proxy)
                print(f"request is failed by proxy ip {proxy}")
    def run(self):
        print("tester is begining")
        try:
            count = self.redis.count()
            print(f"hold {count} proxies")
            for i in range(0, count, BATCH_TEST_SIZE):
                start = i
                stop = min(i+BATCH_TEST_SIZE, count)
                print(f"will test {start+1} - {stop} proxies")
                test_proxies = self.redis.batch(start, stop)
                loop = asyncio.get_event_loop()
                tasks = [self.test_single_proxy(proxy) for proxy in test_proxies]
                loop.run_until_complete(asyncio.wait(tasks))
                sys.stdout.flush()
                time.sleep(5)
        except Exception as e:
            print(f"test error, {e.args}")