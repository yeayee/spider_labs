# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Douban250Item(scrapy.Item):
    ranking = scrapy.Field() # 排名
    name = scrapy.Field() # 电影名
    score = scrapy.Field() # 评分
    score_num = scrapy.Field() # 评论人数
    quote = scrapy.Field() # 一句短评
    cover_url = scrapy.Field() # 链接
