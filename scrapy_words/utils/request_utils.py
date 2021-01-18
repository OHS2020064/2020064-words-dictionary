import json

import grequests

from scrapy_words.configs import scrapy_configs
from scrapy_words.utils.logger_utils import logger


def err_handler(request, exception):
    if scrapy_configs.configs('debug'):
        logger.error(exception)


def get(url):
    if scrapy_configs.configs('debug'):
        logger.info(url)
    req_list = [grequests.request("GET",
                                  url=url,
                                  headers=scrapy_configs.configs('api_headers'),
                                  timeout=10)]
    return grequests.imap(req_list, exception_handler=err_handler)


def post(url, item):
    if scrapy_configs.configs('debug'):
        # logger.info(api_url)
        logger.info(json.dumps(item, ensure_ascii=False))
    req_list = [grequests.request("POST",
                                  url=url,
                                  data=json.dumps(item),
                                  headers=scrapy_configs.configs('api_headers'),
                                  timeout=10)]
    return grequests.imap(req_list, exception_handler=err_handler)


url = "http://127.0.0.1:8008/collecter/Metadata/?recode_id=002594&metadata_name=stock_to_board"
# pp = get(url)
# # print(pp)
#
# for resp in pp:
#     json_ls = json.loads(resp.content)
#
#     # theme_name = concepts_str[0]
# print(json_ls)

# def read_csv():
    # json_ls = []
# for resp in get(url):
#     print(resp,2)
#     json_ls = json.loads(resp.content)
#     print(json_ls)
# bb = read_csv()
# print(bb, 1)
# print(bb.get('data'))
# # for i in bb:
# #     print(i)
#     # j =i[0]
#     # print(j)
# import requests
# res = requests.get(url)
# # print(json.loads(res.content))
# # resp = get(url)
# # json_ls = json.loads(resp.content)
# # print(json_ls)
# json_ls = []
# for resp in get(url ):
#     json_ls = json.loads(resp.content)
# # return json_ls
# # print(json_ls.get('data')[0]['content'].append('tt'))
# print(type(json_ls.get('data')[0]['content']))
# op = json_ls.get('data')[0]['content']
# op.append(1)
# print(op)
