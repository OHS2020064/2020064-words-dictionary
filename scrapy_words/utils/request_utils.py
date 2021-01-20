import json

import grequests

from scrapy_words.configs import scrapy_configs
from scrapy_words.utils.logger_utils import logger


def err_handler(request, exception):
    if scrapy_configs.configs('debug'):
        logger.error(exception)


def get(url, headers=scrapy_configs.configs('headers')):
    if scrapy_configs.configs('debug'):
        logger.info(url)
    req_list = [grequests.request("GET",
                                  url=url,
                                  headers=headers,
                                  timeout=10)]
    return grequests.imap(req_list, exception_handler=err_handler)


def post(url, item, headers=scrapy_configs.configs('headers')):
    if scrapy_configs.configs('debug'):
        logger.info(url)
        logger.info(json.dumps(item, ensure_ascii=False))
    req_list = [grequests.request("POST",
                                  url=url,
                                  data=json.dumps(item),
                                  headers=headers,
                                  timeout=10)]
    return grequests.imap(req_list, exception_handler=err_handler)
