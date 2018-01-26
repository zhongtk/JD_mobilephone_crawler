#-*- coding: UTF-8 -*- 
'''
将京东手机页面商品的图片下载到本地，python版本2.7
Reference: "Web Scraping with Python" 中文版：用Python写网络爬虫
'''
import re
import urlparse
import urllib2
import urllib
import time,datetime
import lxml.html
import itertools

#延迟程序
class Throttle:

    def __init__(self, delay):
        self.delay = delay
        self.domains = {}
    
    def wait(self, url):
        domain = urlparse.urlparse(url).netloc
        last_accessed = self.domains.get(domain)
        
        if self.delay > 0 and last_accessed is not None:
            sleep_secs = self.delay - (datetime.datetime.now() - last_accessed).seconds
            if sleep_secs > 0:
                time.sleep(sleep_secs)
        self.domains[domain] = datetime.datetime.now()

#下载网页程序，考虑代理，重试下载
def download(url,user_agent='wswp',proxy=None, num_retries=2):
    print 'Downloading:', url
    headers = {'User-agent': user_agent}
    request = urllib2.Request(url, headers=headers)
    
    opener = urllib2.build_opener()
    if proxy:
        proxy_params = {urlparse.urlparse(url).scheme: proxy}
        opener.add_handler(urllib2.ProxyHandler(proxy_params))
    try:
        html = opener.open(request).read()
    except urllib2.URLError as e:
        print 'Download error:', e.reason
        html = None
        if num_retries > 0:
            if hasattr(e, 'code') and 500 <= e.code <600:
            # retry 5XXX HTTP error
                html = download(url, user_agent, proxy, num_retries-1)
    return html

if __name__ =="__main__":

    headers = ('User-Agent','Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11')
    for i in range(1,3,1): #翻页
        url = "https://list.jd.com/list.html?cat=9987,653,655&page="+str(i)
        throttle = Throttle(5)
        throttle.wait(url)
#        time.sleep(5)
        html = download(url,headers, None, 2)
        tree = lxml.html.fromstring(html)
        try:
#            print tree.cssselect('li.gl-item>div>div>a>img')   #返回的是字典类型 [<Element img at 0x2cbf6f0>, <Element img at 0x2cbf720>...
            for j in itertools.count(0,1): #迭代器生成
                if tree.cssselect('li.gl-item>div>div>a>img')[j].get('src') != None:
                    img = "https:" + tree.cssselect('li.gl-item>div>div>a>img')[j].get('src')
                    print img
                else:
                    img = "https:" + tree.cssselect('li.gl-item>div>div>a>img')[j].get('data-lazy-img')
                    print img
                #下载图片到本地
                urllib.urlretrieve(img,'F:\pythonProject\jd\pic\p%s-%s.jpg'%(i,j+1)) 
        except:
            continue
