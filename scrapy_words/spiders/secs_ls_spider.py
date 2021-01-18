"""
证券公司列表
"""
import json

import scrapy

from scrapy_words.items.dict_item import DictItem
from scrapy_words.spiders.base_spider import BaseSpider


def create_headers():
    return {
        'Content-Type': 'application/x-www-form-urlencoded',
        'Cookie': 'acw_tc=707c9fd016105912157546537e30a36b628f1d9c2276e074988b266f0f913f; '
                  'BIGipServerjigou=3142691008.20480.0000; '
                  'JSESSIONID=irf-t6X5iw1RpTimild8stHWPOICfhJIPU7U-qoH0OpGpKIMq3cV!673847390 '
    }
    pass


def create_body():
    return {
        'filter_EQS_O#otc_id': '01',
        'filter_EQS_O#sac_id': '',
        'filter_LIKES_aoi_name': '',
        'sqlkey': 'publicity',
        'sqlval': 'ORG_BY_TYPE_INFO'
    }


class SecsLSSpider(BaseSpider):

    name = 'secs_list'

    def start_requests(self):
        super().start_requests()
        return [scrapy.FormRequest(self.start_urls[0],
                                   headers=create_headers(),
                                   formdata=create_body(),
                                   callback=self.parse), ]

    def parse(self, response, **kwargs):
        results = []
        json_ls = json.loads(response.body.decode())
        for json_result in json_ls:
            dict_item = DictItem()
            dict_item['word'] = json_result['AOI_NAME']
            dict_item['word_level'] = 110
            dict_item['pos'] = 'n'
            results.append(dict_item)
        return results

    def parse_cats(self, response):
        print(self.name)
        for td in response.xpath('//*[@id="bodyContent"]/table/tbody/tr/td'):
            for h3 in td.xpath('.//h3'):
                print(h3.xpath('.//text()').extract_first())
        pass
