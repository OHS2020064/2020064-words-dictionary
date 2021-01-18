# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
import os
import csv

from scrapy_words.configs import scrapy_configs
from scrapy_words.utils import datetime_utils


class ScrapyIdxCsvPipeline(object):
    data_path = ''
    files = {}
    writers = {}

    def __init__(self):
        pass

    def open_spider(self, spider):
        if scrapy_configs.configs('file_output', spider.name):
            # csv文件的位置,无需事先创建
            date = datetime_utils.current_date()
            self.data_path = scrapy_configs.configs('file_output_path')
            if not os.path.exists(self.data_path):
                os.mkdir(self.data_path)
            self.data_path = os.path.join(self.data_path, date)
            if not os.path.exists(self.data_path):
                os.mkdir(self.data_path)

    def close_spider(self, spider):
        # 关闭爬虫时顺便将文件保存退出
        for file_key in self.files:
            self.files[file_key].close()

    def process_item(self, item, spider):
        if not scrapy_configs.configs('file_output', spider.name):
            return item
        if item.name not in self.files:
            store_file_path = os.path.join(self.data_path, item.name + datetime_utils.current_datetime() + '.csv')
            self.files[item.name] = open(store_file_path, 'a+', encoding="utf-8", newline='')
            self.writers[item.name] = csv.writer(self.files[item.name], dialect="excel")
            dict_item = vars(item)['_values']
            # csv head
            self.writers[item.name].writerow(dict_item)
        # 判断字段值不为空再写入文件
        if item is not None:
            # 主要是解决存入csv文件时出现的每一个字以','隔离
            dict_item = vars(item)['_values']
            write_value = []
            for name in dict_item:
                if isinstance(dict_item[name], (list, tuple)) and len(dict_item[name]) == 1:
                    value = dict_item[name][0]
                elif isinstance(dict_item[name], (list, tuple)) and len(dict_item[name]) == 0:
                    value = ''
                else:
                    value = dict_item[name]
                write_value.append(str(value))
            # logger.info('writing: ', write_value)
            self.writers[item.name].writerow(write_value)
        return item
