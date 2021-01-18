# Scrapy configs
import os

from scrapy.utils.project import get_project_settings

from scrapy_words.configs.mba_configs import mba_default
from scrapy_words.configs.securities_ls_configs import securities_ls_default

BOT_NAME = 'scrapy_words'

LOG_LEVEL = 'INFO'
DOWNLOADER_MIDDLEWARES = {
    'scrapy_words.middlewares.agent_middleware.RotateUserAgentMiddleware': 400,  # 切换agent
    'scrapy_words.middlewares.auto_proxy_middleware.AutoProxyMiddleware': 543,  # 代理池
}
ITEM_PIPELINES = {
    'scrapy_words.pipelines.pipelines_csv.ScrapyIdxCsvPipeline': 300,
    'scrapy_words.pipelines.pipelines_request.ScrapyIdxRequestPipeline': 800,
}

SPIDER_MODULES = ['scrapy_words.spiders']
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 ' \
             'Safari/537.36 '
DOWNLOAD_DELAY = 2
COOKIES_ENABLED = False
AUTO_PROXY = {  # 代理池中间件设置，详见Github
    'ban_code': [500, 502, 503, 400, 504],
    'init_valid_proxies': 2,
}

DEVELOP = False

FILE_OUTPUT = True
API_OUTPUT = False
FILE_OUTPUT_PATH = os.path.join(os.path.abspath('./'), 'exports')

# spider default config
MBA = mba_default
SECS_LIST = securities_ls_default


def configs(config_name, spider_name=None):
    settings = get_project_settings()
    # config from settings
    if spider_name is None:
        return settings.get(config_name.upper())
    spider_default = settings.get(spider_name.upper())
    if spider_default is not None and config_name in spider_default:
        return spider_default[config_name]
    else:
        return configs_from_os(config_name, settings)
    pass


def configs_from_os(config_name, settings):
    if config_name in os.environ:
        return os.environ[config_name]
    else:
        return settings.get(config_name.upper())
