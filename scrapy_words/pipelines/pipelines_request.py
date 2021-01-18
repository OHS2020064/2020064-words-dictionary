# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import grequests

from scrapy_words.configs import scrapy_configs
from scrapy_words.utils.logger_utils import logger


def err_handler(request, exception):
    if scrapy_configs.configs('debug'):
        logger.error(exception)


def post_api(api_url, item):
    if scrapy_configs.configs('debug'):
        logger.info(api_url)
        logger.info(json.dumps(item.to_request_obj(), ensure_ascii=False))
    req_list = [grequests.request("POST",
                                  url=api_url,
                                  data=json.dumps(item.to_request_obj()),
                                  headers=scrapy_configs.configs('api_headers'),
                                  timeout=10)]
    grequests.map(req_list, exception_handler=err_handler)


class ScrapyIdxRequestPipeline(object):
    process = False

    def __init__(self):
        pass

    def open_spider(self, spider):
        self.process = True
        pass

    def close_spider(self, spider):
        self.process = False
        pass

    def process_item(self, item, spider):
        self.process = True
        if not scrapy_configs.configs('api_output', spider.name):
            return item
        try:
            if isinstance(item, (list, tuple)):
                api_url = scrapy_configs.configs(item[0].name + '_api', spider.name)
            else:
                api_url = scrapy_configs.configs(item.name + '_api', spider.name)
            if api_url == '':
                return item
            api_prefix = scrapy_configs.configs('api_prefix') + scrapy_configs.configs('api_domain')
            port = scrapy_configs.configs('api_port')

            # staging下请求django服务的前缀和端口
            staging_api_prefix = scrapy_configs.configs('api_prefix') + scrapy_configs.configs('staging_api_domain')
            staging_port = scrapy_configs.configs('staging_api_port')
            # product下请求django服务的前缀和端口
            product_api_prefix = scrapy_configs.configs('api_prefix') + scrapy_configs.configs('product_api_domain')
            product_port = scrapy_configs.configs('product_api_port')  # 直接使用域名的话不需要端口

            if port is not None and port != '':
                api_prefix += (':' + port)
            url_prefix = scrapy_configs.configs('url_prefix')
            # staging下django服务的完整url地址
            staging_api_url = (staging_api_prefix + (':' + staging_port) + '/' + url_prefix + '/' + api_url)
            # product下django服务的完整url地址
            product_api_url = (product_api_prefix + '/' + url_prefix + '/' + api_url)
            # 测试环境下django服务的完整url地址
            api_url = (api_prefix + '/' + url_prefix + '/' + api_url)

            if isinstance(item, (list, tuple)):
                for single_item in item:
                    post_api(api_url, single_item)
                    # post_api(staging_api_url, single_item)
                    # post_api(product_api_url, single_item)
            else:
                post_api(api_url, item)
                # post_api(staging_api_url, item)
                # post_api(product_api_url, item)
        except KeyError as e:
            pass
        return item
