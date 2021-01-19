"""
MBA智库
"""
import scrapy

from scrapy_words.items.mba_word_item import MBAWordItem
from scrapy_words.spiders.base_spider import BaseSpider


def create_headers():
    return {
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,'
                  '*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9',
        'Cookie': 's_id=d41d8cd98f00b204e9800998ecf8427e; '
                  '__gads=ID=699b59974df2b4fa-220d7fa292c50078:T=1610102079:RT=1610102079:S'
                  '=ALNI_MaBmRfS9cjv0fcqC5O9qt43pgTJ2g; Hm_lvt_96771760d942f755aa887b0b28d1c30a=1610101484,'
                  '1610440334,1610513472,1610960487; Hm_lpvt_96771760d942f755aa887b0b28d1c30a=1610960981 ',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Upgrade-Insecure-Requests': '1'
    }
    pass


class MBASpider(BaseSpider):
    name = 'mba'

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(self.start_urls[0],
                               callback=self.parse), ]

    def parse(self, response, **kwargs):
        results = []
        for i, div in enumerate(response.xpath('//div[@class="headline-2"]')):
            if i > 0:
                continue
            item = MBAWordItem()
            name = div.xpath('.//h2/text()').extract_first()
            item['parent'] = ''
            item['cat'] = ''
            item['word'] = name
            item['word_level'] = 110
            item['pos'] = 'n'
            results.append(item)
            for j, a in enumerate(div.xpath('../div[3]//a')):
                if j > 0:
                    continue
                url = a.xpath('.//@href').extract_first()
                child_item = MBAWordItem()
                child_item['parent'] = name
                child_item['cat'] = 'categories'
                child_item['word'] = a.xpath('.//text()').extract_first()
                child_item['word_level'] = 109
                child_item['pos'] = 'n'
                results.append(child_item)
                results.append(scrapy.Request('https://%s/%s' % (self.configs('allowed_domains')[0], url),
                                              meta=child_item,
                                              headers=create_headers(),
                                              callback=self.parse_words))
        return results

    def parse_words(self, response):
        print('parse_words: %s' % self.name)
        parent_result = response.request.meta
        results = []
        for i, a in enumerate(response.xpath('//tr[@valign="top"]//a')):
            text = a.xpath('.//text()').extract_first()
            if text == '+':
                continue
            child_item = MBAWordItem()
            child_item['parent'] = parent_result['word']
            child_item['cat'] = 'categories'
            child_item['word'] = text
            child_item['word_level'] = parent_result['word_level'] - 1
            child_item['pos'] = 'n'
            results.append(child_item)
        for j, a in enumerate(response.xpath('//div[@class="page_ul"]//a')):
            child_item = MBAWordItem()
            child_item['parent'] = parent_result['word']
            child_item['cat'] = 'word'
            child_item['word'] = a.xpath('.//text()').extract_first()
            child_item['word_level'] = parent_result['word_level'] - 1
            child_item['pos'] = 'n'
            results.append(child_item)
        return results
        pass
