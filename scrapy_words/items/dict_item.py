# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

from scrapy_words.utils import string_utils, decimal_utils


class BaseScrapyItem(scrapy.Item):
    name = 'scrapy'

    # define the fields for your item here like:
    pass

    def get_str(self, key, default=''):
        if key in self:
            return string_utils.to_string(self[key])
        else:
            return default

    def get_decimal(self, key, default=0):
        if key in self:
            return decimal_utils.to_decimal(self[key])
        else:
            return default


class DictItem(BaseScrapyItem):
    name = 'dict'

    # define the fields for your item here like:
    word = scrapy.Field()
    word_level = scrapy.Field()
    pos = scrapy.Field()

    def to_request_obj(self):
        trans_data = {
            'word': self.get_str('word'),
            'word_level': self.get_str('word_level'),
            'pos': self.get_str('pos')
        }
        return trans_data
