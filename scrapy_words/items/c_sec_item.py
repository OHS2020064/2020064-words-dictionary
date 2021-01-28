"""
中国证券投资基金业协会
"""
import scrapy

from scrapy_words.items.dict_item import DictItem


class CSec21Item(DictItem):
    """基金协会会员单位"""
    name = 'c_sec_2_1'

    parent = scrapy.Field()
    cat = scrapy.Field()

    def to_request_obj(self):
        trans_data = super().to_request_obj()
        trans_data['parent'] = self.get_str('parent')
        trans_data['cat'] = self.get_str('cat')
        return trans_data


class CSec22Item(CSec21Item):
    """私募基金管理人产品"""
    name = 'c_sec_2_2'


class CSec23Item(CSec21Item):
    """券商集合资管"""
    name = 'c_sec_2_3'


class CSec24Item(CSec21Item):
    """证券公司私募产品"""
    name = 'c_sec_2_4'


class CSec25Item(CSec21Item):
    """私募基金管理人"""
    name = 'c_sec_2_5'
