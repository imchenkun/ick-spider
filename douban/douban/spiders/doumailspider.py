# -*- coding:utf-8 -*-
'''by sudo rm -rf  http://imchenkun.com'''
import scrapy
from faker import Factory
from douban.items import DoubanMailItem
import urlparse
f = Factory.create()


class MailSpider(scrapy.Spider):
    name = 'douban-mail'
    allowed_domains = ['accounts.douban.com', 'douban.com']
    start_urls = [
        'https://www.douban.com/'
    ]

    headers = {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
        'Connection': 'keep-alive',
        'Host': 'accounts.douban.com',
        'User-Agent': f.user_agent()
    }

    formdata = {
        'form_email': '您的账号',
        'form_password': '您的密码',
        # 'captcha-solution': '',
        # 'captcha-id': '',
        'login': '登录',
        'redir': 'https://www.douban.com/',
        'source': 'None'
    }

    def start_requests(self):
        return [scrapy.Request(url='https://www.douban.com/accounts/login',
                               headers=self.headers,
                               meta={'cookiejar': 1},
                               callback=self.parse_login)]

    def parse_login(self, response):
        # 如果有验证码要人为处理
        if 'captcha_image' in response.body:
            print 'Copy the link:'
            link = response.xpath('//img[@class="captcha_image"]/@src').extract()[0]
            print link
            captcha_solution = raw_input('captcha-solution:')
            captcha_id = urlparse.parse_qs(urlparse.urlparse(link).query, True)['id']
            self.formdata['captcha-solution'] = captcha_solution
            self.formdata['captcha-id'] = captcha_id
        return [scrapy.FormRequest.from_response(response,
                                                 formdata=self.formdata,
                                                 headers=self.headers,
                                                 meta={'cookiejar': response.meta['cookiejar']},
                                                 callback=self.after_login
                                                 )]

    def after_login(self, response):
        print response.status
        self.headers['Host'] = "www.douban.com"
        return scrapy.Request(url='https://www.douban.com/doumail/',
                              meta={'cookiejar': response.meta['cookiejar']},
                              headers=self.headers,
                              callback=self.parse_mail)

    def parse_mail(self, response):
        print response.status
        for item in response.xpath('//div[@class="doumail-list"]/ul/li'):
            mail = DoubanMailItem()
            mail['sender_time'] = item.xpath('div[2]/div/span[1]/text()').extract()[0]
            mail['sender_from'] = item.xpath('div[2]/div/span[2]/text()').extract()[0]
            mail['url'] = item.xpath('div[2]/p/a/@href').extract()[0]
            mail['title'] = item.xpath('div[2]/p/a/text()').extract()[0]
            print mail
            yield mail