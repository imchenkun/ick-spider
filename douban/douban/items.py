# -*- coding: utf-8 -*-
'''by sudo rm -rf  http://imchenkun.com'''
import scrapy


class DoubanBookItem(scrapy.Item):
    name = scrapy.Field()            # 书名
    price = scrapy.Field()           # 价格
    edition_year = scrapy.Field()    # 出版年份
    publisher = scrapy.Field()       # 出版社
    ratings = scrapy.Field()         # 评分


class DoubanMailItem(scrapy.Item):
    sender_time = scrapy.Field()     # 发送时间
    sender_from = scrapy.Field()     # 发送人
    url = scrapy.Field()             # 豆邮详细地址
    title = scrapy.Field()           # 豆邮标题