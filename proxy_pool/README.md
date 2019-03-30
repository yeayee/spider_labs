proxy_pool相关说明
- db:是Redis库，用于存储proxy
- crawler:爬取各个免费网站的proxy
- getter:调用crawler和db，协调爬取proxy和入库操作
- tester:不断去测试proxy的可用性
- api:基于flask开放接口，用于提供可用的proxy
- scheduler:协调爬取过程，测试过程，api过程的逻辑
- utils:下载工具函数
- setting:配置文件
- run:运行系统的入口： python run.py