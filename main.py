import os

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import scrapy_words.configs
import scrapy_words.items
import scrapy_words.middlewares
import scrapy_words.pipelines
import scrapy_words.utils
import scrapy_words.spiders


def main(spider_name='mba'):
    settings = get_project_settings()
    spiders = {
        'mba': scrapy_words.spiders.mba_spider.MBASpider,
        'secs_list': scrapy_words.spiders.secs_ls_spider.SecsLSSpider,
    }
    spider = spiders[spider_name]
    for (k, v) in spiders.items():
        if 'spider' in os.environ and k == os.environ['spider']:
            spider = v
            break

    process = CrawlerProcess(settings=settings)
    process.crawl(spider)
    process.start()
    pass


if __name__ == '__main__':
    main('mba')
