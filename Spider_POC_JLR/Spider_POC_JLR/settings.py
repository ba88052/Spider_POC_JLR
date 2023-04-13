from webdriver_manager.chrome import ChromeDriverManager
import os
# Scrapy settings for Spider_POC_JLR project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://docs.scrapy.org/en/latest/topics/settings.html
#     https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://docs.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = "Spider_POC_JLR"

SPIDER_MODULES = ["Spider_POC_JLR.spiders"]
NEWSPIDER_MODULE = "Spider_POC_JLR.spiders"

#中間件
DOWNLOADER_MIDDLEWARES = {
    'scrapy_selenium.SeleniumMiddleware': 800,
    # 'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 400,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 900,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 970,
}
#更換Proxy IP時，是否同步更換UA，以及更換失敗後的默認UA
RANDOM_UA_PER_PROXY = True
FAKEUSERAGENT_FALLBACK = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'


#Selenium
SELENIUM_DRIVER_NAME = 'chrome'  #瀏覽器名稱
SELENIUM_DRIVER_EXECUTABLE_PATH = ChromeDriverManager().install()
SELENIUM_DRIVER_ARGUMENTS = [
    '--window-size=1920,1080',
    '--disable-gpu',
    '--disable-notifications',
    '--no-sandbox',
    '--disable-dev-shm-usage',
    '--headless'
]

#LOG_FILE
LOG_FILE = "spider_POC_JLR_log.ini"
# LOG_LEVEL = "DEBUG"  #特別注意這邊一定要大寫
LOG_LEVEL = "INFO"  #特別注意這邊一定要大寫

#BQ設定
GCP_PROJECT_ID = 'spider-poc'
BQ_DATASET_ID = 'spider_poc_jlr'
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spider-poc-gcp-key.json"
# Enable the BigQueryPipeline
ITEM_PIPELINES = {'Spider_POC_JLR.pipelines.BigQueryPipeline': 1}

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = "Spider_POC_JLR (+http://www.yourdomain.com)"

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 100

# Configure a delay for requests for the same website (default: 0)
# See https://docs.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 1
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
#    "Accept-Language": "en",
#}

# Enable or disable spider middlewares
# See https://docs.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    "Spider_POC_JLR.middlewares.SpiderPocJlrSpiderMiddleware": 543,
#}

# Enable or disable downloader middlewares
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
#DOWNLOADER_MIDDLEWARES = {
#    "Spider_POC_JLR.middlewares.SpiderPocJlrDownloaderMiddleware": 543,
#}

# Enable or disable extensions
# See https://docs.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    "scrapy.extensions.telnet.TelnetConsole": None,
#}

# Configure item pipelines
# See https://docs.scrapy.org/en/latest/topics/item-pipeline.html
#ITEM_PIPELINES = {
#    "Spider_POC_JLR.pipelines.SpiderPocJlrPipeline": 300,
#}

# Enable and configure the AutoThrottle extension (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://docs.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = "httpcache"
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = "scrapy.extensions.httpcache.FilesystemCacheStorage"

# Set settings whose default value is deprecated to a future-proof value
REQUEST_FINGERPRINTER_IMPLEMENTATION = "2.7"
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
