"""
MBA智库
"""
import scrapy

from scrapy_words.items.mba_word_item import MBAWordItem
from scrapy_words.spiders.base_spider import BaseSpider
from scrapy_words.utils.logger_utils import logger


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
        return [scrapy.Request(self.start_urls[0], callback=self.parse)]

    def parse(self, response, **kwargs):
        results = []
        for i, div in enumerate(response.xpath('//div[@class="headline-2"]')):
            item = MBAWordItem()
            name = div.xpath('.//h2/text()').extract_first()
            item['parent'] = ''
            item['cat'] = ''
            item['word'] = name
            item['word_level'] = 120
            item['pos'] = 'n'
            # results.append(item)
            yield item
            for j, a in enumerate(div.xpath('../div[3]//a')):
                url = a.xpath('.//@href').extract_first()
                logger.info('url: %s' % url)
                child_item = MBAWordItem()
                child_item['parent'] = name
                child_item['cat'] = 'categories'
                child_item['word'] = a.xpath('.//text()').extract_first()
                child_item['word_level'] = 119
                child_item['pos'] = 'n'
                # results.append(child_item)
                yield child_item
                req = scrapy.Request('https://%s%s' % (self.configs('allowed_domains')[0], url),
                                     meta=child_item,
                                     headers=create_headers(),
                                     callback=self.parse_words)
                # results.append(req)
                yield req
        # return results

    def parse_words(self, response):
        parent_result = response.request.meta
        results = []
        for i, a in enumerate(response.xpath('//div[@class="CategoryTreeItem"]//a')):
            text = a.xpath('.//text()').extract_first()
            url = a.xpath('.//@href').extract_first()
            if text == '+' or len(url) < 20:
                continue
            logger.info('parse_words: %s' % response.request.url)
            logger.info('url: %s' % url)
            child_item = MBAWordItem()
            child_item['parent'] = parent_result['word']
            child_item['cat'] = 'categories'
            child_item['word'] = text
            child_item['word_level'] = parent_result['word_level'] - 1
            child_item['pos'] = 'n'
            # results.append(child_item)
            yield child_item
            req = scrapy.Request('https://%s%s' % (self.configs('allowed_domains')[0], url),
                                 meta=child_item,
                                 headers=create_headers(),
                                 callback=self.parse_words)
            # results.append(req)
            yield req
        for j, a in enumerate(response.xpath('//div[@class="page_ul"]//a')):
            child_item = MBAWordItem()
            child_item['parent'] = parent_result['word']
            child_item['cat'] = 'word'
            child_item['word'] = a.xpath('.//text()').extract_first()
            child_item['word_level'] = parent_result['word_level'] - 1
            child_item['pos'] = 'n'
            # results.append(child_item)
            yield child_item
        # return results
        pass
