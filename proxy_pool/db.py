
import re
from random import choice

import redis

from setting import REDIS_HOST, REDIS_KEY, REDIS_PASSWORD, REDIS_PROT
from setting import INITIAL_SCORE, MIN_SCORE, MAX_SCORE


class PoolEmptyError(Exception):
    def __init__(self):
        Exception.__init__(self)
    
    def __str__(self):
        return repr(f"Proxy Pool is Empty!")

class RedisClient:
    def __init__(self, host=REDIS_HOST, port=REDIS_PROT, password=REDIS_PASSWORD):
        self.db = redis.StrictRedis(host=host, port=port, password=password,decode_responses=True)
    
    def add(self, proxy, score=INITIAL_SCORE):
        """添加代理， 设置为初始分值"""
        if not re.match("\d+.\d+.\d+.\d+\:\d+", proxy):
            print(f"Proxy is not format, {proxy} is ignore.")
            return
        if not self.db.zscore(REDIS_KEY, proxy):
            print(type(score))
            return self.db.zadd(REDIS_KEY, score, proxy)
    
    def random(self):
        """
        随机选一个代理
        """
        result = self.db.zrangebyscore(REDIS_KEY, MAX_SCORE, MAX_SCORE)
        if len(result):
            return choice(result)
        else:
            result = self.db.zrevrange(REDIS_KEY, 0, 100)
            if len(result):
                return choice(result)
            else:
                raise PoolEmptyError
    
    def decrease(self, proxy):
        score = self.db.zscore(REDIS_KEY, proxy)
        if score and score > MIN_SCORE:
            print(f"proxy {proxy}'s score is {score} -1")
            return self.db.zincrby(REDIS_KEY, proxy, -1)
        else:
            print(f"proxy {proxy} is removing")
            return self.db.zrem(REDIS_KEY, proxy)
    
    def exists(self, proxy):
        return not self.db.zscore(REDIS_KEY, proxy) == None
    
    def max(self, proxy):
        print(f"proxy {proxy} can useing, score is setting to {MAX_SCORE}")
        return self.db.zadd(REDIS_KEY, MAX_SCORE, proxy)
    
    def count(self):
        return self.db.zcard(REDIS_KEY)
    
    def all(self):
        return self.db.zrangebyscore(REDIS_KEY, MIN_SCORE, MAX_SCORE)
    
    def batch(self, start, stop):
        return self.db.zrevrange(REDIS_KEY, start, stop-1)

if __name__ == "__main__":
    conn = RedisClient()
    result = conn.batch(0, 100)
    print(result)
