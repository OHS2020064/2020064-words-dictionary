# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy_words.items.dict_item import DictItem


class MBAWordItem(DictItem):
    name = 'mba_word'
