# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy

from scrapy_words.items.dict_item import DictItem


class MBAWordItem(DictItem):
    name = 'mba_word'

    # define the fields for your item here like:
    cat = scrapy.Field()

    def to_request_obj(self):
        trans_data = super().to_request_obj()
        trans_data['cat'] = self.get_str('cat')
        return trans_data
