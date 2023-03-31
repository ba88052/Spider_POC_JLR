# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class SpiderPocJlrLinkItem(scrapy.Item):
    START_DATE = scrapy.Field()
    END_DATE = scrapy.Field()
    JLR_LINK = scrapy.Field()
    JLR_TITLE = scrapy.Field()



class SpiderPocJlrPdfItem(scrapy.Item):
    DECISION_NAME = scrapy.Field()
    LEGAL_RELATIONSHIP = scrapy.Field()
    JUDGMENT_LEVEL = scrapy.Field()
    TYPE_OF_CASE = scrapy.Field()
    TRIAL_COURT = scrapy.Field()
    APPLICATION_OF_PRECEDENT = scrapy.Field()
    CORRECTIONS = scrapy.Field()
    INFORMATION_ABOUT_THE_CASE = scrapy.Field()
    TOTAL_NUMBER_OF_VOTES_VOTED_AS_THE_SOURCE_OF_CASE_LAW_DEVELOPMENT = scrapy.Field() 
    PDF_TEXT = scrapy.Field() 

