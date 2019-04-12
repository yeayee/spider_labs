# -*- coding: UTF-8 -*-

import config
from mysql_wrapper_sync import Connection
import lzma

db = Connection(config.db_host, config.db_name, config.db_username, config.db_password)

sql = "select * from crawler_hub"
data = db.query(sql)
print("data in crawler_hub", "-" * 100)
print(len(data), data)

sql = "select * from crawler_html"
data = db.query(sql)
print("data in crawler_html", "-" * 100)
print(len(data))
for d in data:
    html = d[3]
    # html = lzma.decompress(html)
    # print(html.decode("utf8"))
    print(html)
