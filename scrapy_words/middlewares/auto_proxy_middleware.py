#! -*- coding: utf-8 -*-
import urllib.request
import threading
import math
import re
import time
from urllib.error import HTTPError

from bs4 import BeautifulSoup
from twisted.internet import defer
from twisted.internet.error import TimeoutError, ConnectionRefusedError, \
    ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone

from scrapy_words.utils import request_utils
from scrapy_words.utils.logger_utils import logger


class AutoProxyMiddleware(object):
    EXCEPTIONS_TO_CHANGE = (defer.TimeoutError, TimeoutError, ConnectionRefusedError,
                            ConnectError, ConnectionLost, TCPTimedOutError, ConnectionDone)

    _settings = [
        ('enable', True),
        ('test_urls', [('http://www.w3school.com.cn', '06004630'), ]),
        ('test_proxy_timeout', 5),
        ('download_timeout', 60),
        ('test_thread_nums', 20),
        ('ban_code', [503, ]),
        ('ban_re', r''),
        ('proxy_least', 3),
        ('init_valid_proxies', 1),
        ('invalid_limit', 200),
    ]

    def __init__(self, proxy_set=None):
        self.enable = True
        self.init_valid_proxies = 1
        self.test_thread_nums = 20
        self.proxy_least = 3
        self.invalid_limit = 200
        self.ban_re = r''
        self.ban_code = [503, ]
        self.download_timeout = 60
        self.test_urls = [('http://www.w3school.com.cn', '06004630'), ]
        self.test_proxy_timeout = 10

        self.proxy_set = proxy_set or {}
        # for k, v in self._settings:
        #     setattr(self, k, self.proxy_set.get(k, v))

        # 代理列表和当前的代理指针，couter_proxy用作该代理下载的网页数量
        self.proxy = []
        self.proxy_index = 0
        self.proxies = {}
        self.counter_proxy = {}

        self.fetch_new_proxy()
        if self.proxies:
            self.test_proxies(self.proxies, wait=True)
        logger.info('Use proxy : %s', self.proxy)

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings.getdict('AUTO_PROXY'))

    def process_request(self, request, spider):
        if not self._is_enabled_for_request(request):
            return

        if self.len_valid_proxy() > 0:
            self.set_proxy(request)
            # if 'download_timeout' not in request.meta:
            request.meta['download_timeout'] = self.download_timeout
        else:
            # 没有可用代理，直连
            if 'proxy' in request.meta:
                del request.meta['proxy']

    def process_response(self, request, response, spider):
        if not self._is_enabled_for_request(request):
            return response

        if response.status in self.ban_code:
            self.invalid_proxy(request.meta['proxy'])
            logger.debug("Proxy[%s] ban because return http status code:[%s]. ",
                         request.meta['proxy'], str(response.status))
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

        if self.ban_re:
            try:
                pattern = re.compile(self.ban_re)
            except TypeError:
                logger.error('Wrong "ban_re", please check settings')
                return response
            match = re.search(pattern, response.body)
            if match:
                self.invalid_proxy(request.meta['proxy'])
                logger.debug("Proxy[%s] ban because pattern match:[%s]. ", request.meta['proxy'], str(match))
                new_request = request.copy()
                new_request.dont_filter = True
                return new_request

        if 'proxy' in request.meta:
            p = request.meta['proxy']
            self.counter_proxy[p] = self.counter_proxy.setdefault(p, 1) + 1
        return response

    def process_exception(self, request, exception):

        from twisted.internet.error import TimeoutError
        if isinstance(exception, self.EXCEPTIONS_TO_CHANGE) \
                and request.meta.get('proxy', False):
            self.invalid_proxy(request.meta['proxy'])
            logger.debug("Proxy[%s] connect exception[%s].", request.meta['proxy'], exception)
            new_request = request.copy()
            new_request.dont_filter = True
            return new_request

        elif isinstance(exception, TimeoutError):
            print('TimeoutError了,此时返回request')
            # return request
        elif isinstance(exception, TypeError):
            print('TypeError,此时返回request')
            # return request

    def invalid_proxy(self, proxy):
        """
        将代理设为invalid。如果之前该代理已下载超过200页（默认）的资源，则暂时不设置，仅切换代理，并减少其计数。
        """
        if self.counter_proxy.get(proxy, 0) > self.invalid_limit:
            self.counter_proxy[proxy] = self.counter_proxy.get(proxy, 0) - 50
            if self.counter_proxy[proxy] < 0:
                self.counter_proxy[proxy] = 0
            self.change_proxy()
        else:
            self.proxies[proxy] = False
            # logger.info('Set proxy[%s] invalid.', proxy)

    def change_proxy(self):
        """
        切换代理。
        """
        while True:
            self.proxy_index = (self.proxy_index + 1) % len(self.proxy)
            proxy_valid = self.proxies[self.proxy[self.proxy_index]]
            if proxy_valid:
                break
            if self.len_valid_proxy() == 0:
                logger.info('Available proxies is none.Waiting for fetch new proxy.')
                break
        logger.info('Change proxy to %s', self.proxy[self.proxy_index])
        logger.info('Available proxies[%s]: %s', self.len_valid_proxy(), self.valid_proxies())

        # 可用代理数量小于预设值则扩展代理
        if self.len_valid_proxy() < self.proxy_least:
            self.extend_proxy()

    def set_proxy(self, request):
        """
        设置代理。
        """
        proxy_valid = self.proxies[self.proxy[self.proxy_index]]
        if not proxy_valid:
            self.change_proxy()

        request.meta['proxy'] = self.proxy[self.proxy_index]
        # logger.info('Set proxy. request.meta: %s', request.meta)

    def len_valid_proxy(self):
        """
        计算可用代理的数量
        """
        count = 0
        for p in self.proxy:
            if self.proxies[p]:
                count += 1
        return count

    def valid_proxies(self):
        """
        可用代理列表
        """
        proxies = []
        for p in self.proxy:
            if self.proxies[p]:
                proxies.append(p)
        return proxies

    def extend_proxy(self):
        """
        扩展代理。测试代理是异步的。
        """
        self.fetch_new_proxy()
        self.test_proxies(self.proxies)

    def append_proxy(self, p):
        """
        辅助函数，将测试通过的代理添加到列表
        """
        if p not in self.proxy:
            self.proxy.append(p)

    def fetch_new_proxy(self):
        """
        获取新的代理，目前从三个网站抓取代理，每个网站开一个线程抓取代理。
        """
        logger.info('Starting fetch new proxy.')
        # urls = ['xici', 'ip3336', 'kxdaili', 'xil']
        urls = ['xil']
        threads = []
        for url in urls:
            t = ProxyFetch(self.proxies, url)
            threads.append(t)
            t.start()
        for t in threads:
            t.join()

    def test_proxies(self, proxies, wait=False):
        """
        测试代理可通性。测试网址、特征码以及测试线程数均可设置。
        """
        list_proxy = proxies.items()
        threads = []
        n = int(math.ceil(len(list_proxy) / self.test_thread_nums))
        for i in range(self.test_thread_nums):
            # 将待测试的代理平均分给测试线程
            list_part = list(list_proxy)[i * n: (i + 1) * n]
            part = {k: v for k, v in list_part}
            t = ProxyValidate(self, part)
            threads.append(t)
            t.start()

        try:
            self.ensure_has_valid_proxy(wait, threads)
        except Exception as e:
            logger.info(e)

    def ensure_has_valid_proxy(self, wait, threads):
        # 初始化该中间件时，等待有可用的代理
        if wait:
            while True:
                for t in threads:
                    t.join(0.2)
                    if self._has_valid_proxy():
                        break
                if self._has_valid_proxy():
                    break

    def _has_valid_proxy(self):
        if self.len_valid_proxy() >= self.init_valid_proxies:
            return True

    def _is_enabled_for_request(self, request):
        return self.enable and 'dont_proxy' not in request.meta


class ProxyValidate(threading.Thread):
    """
    测试代理线程类
    """

    def __init__(self, auto_proxy, part):
        super(ProxyValidate, self).__init__()
        self.auto_proxy = auto_proxy
        self.part = part

    def run(self):
        self.test_proxies(self.part)

    def test_proxies(self, proxies):
        for proxy, valid in proxies.items():
            check_proxy_res = False
            try:
                check_proxy_res = self.check_proxy(proxy)
            except Exception as e:
                logger.info(e)
            if check_proxy_res:
                self.auto_proxy.proxies[proxy] = True
                self.auto_proxy.append_proxy(proxy)

    def check_proxy(self, proxy):
        proxy_handler = urllib.request.ProxyHandler({'http': proxy})
        opener = urllib.request.build_opener(proxy_handler, urllib.request.HTTPHandler)
        try:
            for url, code in self.auto_proxy.test_urls:
                resp = opener.open(url, timeout=self.auto_proxy.test_proxy_timeout).read()
                resp_decode = resp.decode('gbk')
                if code not in resp_decode:
                    return False
            return True
        except Exception as e:
            if e is None:
                logger.error('Failed to check_proxy. Exception[%s]', e)
            return False


def get_soup(url):
    retry_count = 3
    html_doc = None
    while True:
        if retry_count <= 0:
            logger.error('Failed to fetch_proxy_from_xil. retry %i times', retry_count)
            break
        try:
            html_doc = next(request_utils.get(url, headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
                              "Chrome/47.0.2526.106 "
                              "Safari/537.36"
            })).content.decode()
            break
        except Exception as e:
            logger.error("Fetch proxy from {} fail, will try later.".format(url))
            logger.error(e)
            time.sleep(60)
        retry_count = retry_count - 1

    soup = BeautifulSoup(html_doc, features='lxml')
    return soup


class ProxyFetch(threading.Thread):

    def __init__(self, proxies, url):
        super(ProxyFetch, self).__init__()
        self.proxies = proxies
        self.url = url

    def run(self):
        self.proxies.update(getattr(self, 'fetch_proxy_from_' + self.url)())

    def fetch_proxy_from_xil(self):
        logger.info('get proxies from: %s' % self.url)
        proxies = {}
        url = 'http://www.xiladaili.com/'
        try:
            soup = get_soup(url)
            trs = soup.find("table", attrs={"class": "fl-table"}).tbody.find_all("tr")
            for j, tr in enumerate(trs):
                tds = tr.find_all("td")
                td = tds[0].string.strip()
                ip = td.split(':')[0]
                port = td.split(':')[1]
                proxy = ''.join(['http://', ip, ':', port])
                proxies[proxy] = False
        except Exception as e:
            logger.error('Failed to fetch_proxy_from_xil. Exception[%s]', e)
        return proxies

    def fetch_proxy_from_ip3336(self):
        logger.info('get proxies from: %s' % self.url)
        proxies = {}
        url = 'http://www.ip3366.net/free/?stype=1&page='
        try:
            for i in range(1, 6):
                soup = get_soup(url + str(i))
                trs = soup.find("div", attrs={"id": "list"}).table.find_all("tr")
                for j, tr in enumerate(trs):
                    if 0 == j:
                        continue
                    tds = tr.find_all("td")
                    ip = tds[0].string.strip().encode('utf-8')
                    port = tds[1].string.strip().encode('utf-8')
                    proxy = ''.join(['http://', ip.decode(), ':', port.decode()])
                    proxies[proxy] = False
        except Exception as e:
            logger.error('Failed to fetch_proxy_from_ip3336. Exception[%s]', e)
        return proxies

    def fetch_proxy_from_kxdaili(self):
        logger.info('get proxies from: %s' % self.url)
        proxies = {}
        url = 'http://www.kxdaili.com/dailiip/1/%d.html'
        try:
            for i in range(1, 11):
                soup = get_soup(url % i)
                if soup is None:
                    continue
                trs = soup.find("table", attrs={"class": "active"}).find_all("tr")
                for j, tr in enumerate(trs):
                    if 0 == j:
                        continue
                    tds = tr.find_all("td")
                    ip = tds[0].string.strip().encode('utf-8')
                    port = tds[1].string.strip().encode('utf-8')
                    proxy = ''.join(['http://', ip.decode(), ':', port.decode()])
                    proxies[proxy] = False
        except Exception as e:
            logger.error('Failed to fetch_proxy_from_kxdaili. Exception[%s]', e)

        return proxies

    def fetch_proxy_from_xici(self):
        logger.info('get proxies from: %s' % self.url)
        proxies = {}
        url = "http://www.xicidaili.com/nn/"
        try:
            for i in range(1, 4):
                soup = get_soup(url + str(i))
                trs = soup.find("table", attrs={"id": "ip_list"}).find_all("tr")
                for j, tr in enumerate(trs):
                    if 0 == j:
                        continue
                    tds = tr.find_all('td')
                    ip = tds[1].text
                    port = tds[2].text
                    proxy = ''.join(['http://', ip, ':', port]).encode('utf-8')
                    proxies[proxy] = False
        except Exception as e:
            logger.error('Failed to fetch_proxy_from_xici. Exception[%s]', e)

        return proxies


if __name__ == '__main__':
    AutoProxyMiddleware()
