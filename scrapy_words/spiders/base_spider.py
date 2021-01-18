"""
所有爬虫基类
"""

import scrapy

from scrapy_words.configs import scrapy_configs


class BaseSpider(scrapy.Spider):
    """
    提取共用属性如：allowed_domains,start_urls等
    """
    name = 'base'
    allowed_domains = None
    start_urls = None
    next_page = True
    page_num = 1

    def start_requests(self):
        self.allowed_domains = self.configs('allowed_domains')
        self.start_urls = self.configs('start_urls')

    def parse(self, response, **kwargs):
        pass

    def configs(self, config_name):
        return scrapy_configs.configs(config_name, self.name)
        pass
