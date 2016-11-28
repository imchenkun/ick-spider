#-*- coding: utf-8 -*-
import os
import requests
from bs4 import BeautifulSoup
import random
#from faker import Factory
import Queue
import threading

#fake = Factory.create()

luoo_site = 'http://www.luoo.net/music/'
#luoo_site_mp3 = 'http://luoo-mp3.kssws.ks-cdn.com/low/luoo/radio%s/%s.mp3' #luoo CDN地址换了

luoo_site_mp3 = 'http://mp3-cdn.luoo.net/low/luoo/radio%s/%s.mp3'

proxy_ips = [
    '183.129.151.130' # 这里配置可用的代理IP
    ]

headers = {
    'Connection': 'keep-alive',
    #'User-Agent': fake.user_agent() #可以不用fake，写死，不过如果被luoo屏蔽了就要换新的
    'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.99 Safari/537.36'
    }


def random_proxies():
    ip_index = random.randint(0, len(proxy_ips)-1)
    res = { 'http': proxy_ips[ip_index] }
    return res

def fix_characters(s):
    for c in ['<', '>', ':', '"', '/', '\\', '|', '?', '*']:
        s = s.replace(c, '')
    return s


class LuooSpider(threading.Thread):
    def __init__(self, url, vols, queue=None):
        threading.Thread.__init__(self)
        print '[luoo spider]'
        print '=' * 20

        self.url = url
        self.queue = queue
        self.vol = '1'
        self.vols = vols

    def run(self):
        for vol in self.vols:
            self.spider(vol)
        print '\ncrawl end\n\n'
    
    def spider(self, vol):
        url = luoo_site + vol
        print 'crawling: ' + url + '\n'
        #res = requests.get(url, proxies=random_proxies()) #可以不设置代理
        res = requests.get(url)
        
        soup = BeautifulSoup(res.content, 'html.parser')
        title = soup.find('span', attrs={'class': 'vol-title'}).text
        cover = soup.find('img', attrs={'class': 'vol-cover'})['src']
        desc = soup.find('div', attrs={'class': 'vol-desc'})
        track_names = soup.find_all('a', attrs={'class': 'trackname'})
        track_count = len(track_names)
        tracks = []
        for track in track_names:
            _id = str(int(track.text[:2])) if (int(vol) < 12) else track.text[:2]  # 12期前的音乐编号1~9是1位（如：1~9），之后的都是2位 1~9会在左边垫0（如：01~09）
            _name = fix_characters(track.text[4:])
            tracks.append({'id': _id, 'name': _name})

        phases = {
            'phase': vol,                        # 期刊编号
            'title': title,                      # 期刊标题
            'cover': cover,                      # 期刊封面
            'desc': desc,                        # 期刊描述
            'track_count': track_count,          # 节目数
            'tracks': tracks                     # 节目清单(节目编号，节目名称)
            }
        
        self.queue.put(phases)


class LuooDownloader(threading.Thread):
    def __init__(self, url, dist, queue=None):
        threading.Thread.__init__(self)
        self.url = url
        self.queue = queue
        self.dist = dist
        self.__counter = 0
        
    def run(self):
        while True:
            if self.queue.qsize() <= 0:
                pass
            else:
                phases = self.queue.get()
                self.download(phases)

    def download(self, phases):
        for track in phases['tracks']:
            file_url = self.url % (phases['phase'], track['id'])

            local_file_dict = '%s/%s' % (self.dist, phases['phase'])
            if not os.path.exists(local_file_dict):
                os.makedirs(local_file_dict)
            
            local_file = '%s/%s.%s.mp3' % (local_file_dict, track['id'], track['name'])
            if not os.path.isfile(local_file):
                print 'downloading: ' + track['name']
                #res = requests.get(file_url, proxies=random_proxies(), headers=headers)
                print file_url
                
                res = requests.get(file_url, headers=headers)
                with open(local_file, 'wb') as f:
                    f.write(res.content)
                    f.close()
                print 'done.\n'
            else:
                print 'break: ' + track['name']


if __name__ == '__main__':
    spider_queue = Queue.Queue()

    luoo = LuooSpider(luoo_site, vols=['1', '2', '725', '720'], queue=spider_queue)
    luoo.setDaemon(True)
    luoo.start()

    downloader_count = 5
    for i in range(downloader_count):
        luoo_download = LuooDownloader(luoo_site_mp3, 'D:/luoo', queue=spider_queue)
        luoo_download.setDaemon(True)
        luoo_download.start()
