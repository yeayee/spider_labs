# -*- coding: utf-8 -*-
import scrapy
import re
from douban250.items import Douban250Item


class DoubanSpider(scrapy.Spider):
    name = 'douban'
    allowed_domains = ['douban.com']
    start_urls = ['https://movie.douban.com/top250']

    def parse(self, response):
        item = Douban250Item()
        for node in response.xpath("//ol[@class='grid_view']/li"):
            item['ranking'] = node.xpath(".//div[@class='pic']/em/text()").extract()[0]
            item['name'] = node.xpath(".//span[@class='title'][1]/text()").extract()[0]
            item['score']  = node.xpath(".//div[@class='star']/span[2]/text()").extract()[0]
            item['score_num'] = node.xpath(".//div[@class='star']/span[4]/text()").extract()[0]
            if item['score_num']: 
                item['score_num'] = re.findall("[\d]+", item['score_num'])[0]
            item['quote'] = node.xpath(".//p[@class='quote']/span/text()").extract_first()
            item['cover_url'] = node.xpath(".//div[@class='pic']/a/@href").extract()[0]
            
            yield item
            print(item)
        
        next_page = response.xpath("//span[@class='next']/a/@href")
        if next_page:
            url = self.start_urls[0] + next_page.extract_first()
            yield scrapy.Request(url, callback=self.parse)