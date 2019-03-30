# ----- Redis配置
MAX_SCORE = 100
MIN_SCORE = 0
INITIAL_SCORE= 10
REDIS_HOST = "127.0.0.1"
REDIS_PROT = 6379
REDIS_PASSWORD = None
REDIS_KEY = "proxies"

# ----- Getter 配置
GETTER_CYCLE = 300

# ----- Test 配置
TEST_URL = "http://www.baidu.com"
TESTER_CYCLE = 30
VALID_STATUS_CODES = [200, 302]
BATCH_TEST_SIZE = 10

# ----- 系统配置
TESTER_ENABLED = False # 是否开启测试Proxy
GETTER_ENABLED = True # 是否开启爬取Proxy
API_ENABLED = False # 是否开启API接口