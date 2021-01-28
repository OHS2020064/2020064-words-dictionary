import json

import grequests

from scrapy_words.configs import scrapy_configs
from scrapy_words.utils.logger_utils import logger


def err_handler(request, exception):
    if scrapy_configs.configs('debug'):
        logger.error(exception)


def get(url, headers=scrapy_configs.configs('headers'), timeout=(3, 10), g_timeout=None):
    if scrapy_configs.configs('debug'):
        logger.info(url)
    req_list = [grequests.get(url=url,
                              headers=headers,
                              timeout=timeout)]
    if g_timeout is None:
        return grequests.imap(req_list, exception_handler=err_handler)
    else:
        return grequests.map(req_list, exception_handler=err_handler, gtimeout=g_timeout)


def post(url, item, headers=scrapy_configs.configs('headers'), timeout=(3, 10), g_timeout=None):
    if scrapy_configs.configs('debug'):
        logger.info(url)
        logger.info(json.dumps(item, ensure_ascii=False))
    req_list = [grequests.post(url=url,
                               data=json.dumps(item),
                               headers=headers,
                               timeout=timeout)]
    if g_timeout is None:
        return grequests.imap(req_list, exception_handler=err_handler)
    else:
        return grequests.map(req_list, exception_handler=err_handler, gtimeout=g_timeout)
