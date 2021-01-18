"""
MBA智库
"""
import scrapy

from scrapy_words.configs import scrapy_configs
from scrapy_words.items.mba_word_item import MBAWordItem
from scrapy_words.spiders.base_spider import BaseSpider


class MBASpider(BaseSpider):

    name = 'mba'

    def start_requests(self):
        super().start_requests()
        return [scrapy.Request(self.start_urls[0],
                               callback=self.parse), ]

    def parse(self, response, **kwargs):
        results = []
        for div in response.xpath('//div[@class="headline-2"]'):
            item = MBAWordItem()
            item['title'] = div.xpath('.//h2/text()').extract_first()
            for a in div.xpath('../div[3]//a'):
                url = a.xpath('.//@href').extract_first()
                results.append(scrapy.Request('https://%s/%s' % (scrapy_configs.configs('allowed_domains',
                                                                                        self.name)[0],
                                                                 url),
                                              callback=self.parse_cats))
        return results

    def parse_cats(self, response):
        print(self.name)
        for td in response.xpath('//*[@id="bodyContent"]/table/tbody/tr/td'):
            for h3 in td.xpath('.//h3'):
                print(h3.xpath('.//text()').extract_first())
        pass
