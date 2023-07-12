import io
import pdfplumber
import scrapy
import logging
from bs4 import BeautifulSoup
from Spider_POC_JLR.items import SpiderPocJlrPdfItem
from datetime import datetime
import os
import re
from google.cloud import bigquery

today = datetime.today().date()
today = today.strftime("%m%d")

class JudgementInfoSpider(scrapy.Spider):
    bq_table_name = f'jlr_info_max'
    name = "jlr_judgement_info"
    
    def __init__(self,  offset, *args, **kwargs):
        super(JudgementInfoSpider, self).__init__(*args, **kwargs)
        self.offset = offset

#---------------開始Request---------------# 
    def start_requests(self):

        client = bigquery.Client(project="cdcda-lab-377808")
        query =f"""
                SELECT JLR_LINK
                FROM (
                    SELECT DISTINCT JLR_LINK, START_DATE, PAGE
                    FROM `cdcda-lab-377808.SAM_LAB.jlr_link_for_spider_0721`
                )
                ORDER BY START_DATE ASC, PAGE ASC
                LIMIT 10000 OFFSET {self.offset}
            """
        query_job = client.query(query)
        all_jlr_links = [row[0] for row in query_job.result()]
        for jlr_link in all_jlr_links:  
            logging.error(jlr_link)
            # logging.info(f'url is {link}')
            yield scrapy.Request(jlr_link, callback= self.parse_page_data, errback=self.handle_error, cb_kwargs={"jlr_link":jlr_link}) 

#---------------處理資料---------------# 
    def parse_page_data(self, response, jlr_link):
        #處理頁面資訊
        soup = BeautifulSoup(response.body, "html.parser")
        SPIDER_POC_JLR_PDF_ITEM = SpiderPocJlrPdfItem()
        SPIDER_POC_JLR_PDF_ITEM = self.get_page_data(soup, SPIDER_POC_JLR_PDF_ITEM)
        SPIDER_POC_JLR_PDF_ITEM["JLR_LINK"] = jlr_link
        #找到頁面中的PDF連結
        pdf_url_head = "https://congbobanan.toaan.gov.vn/"
        pdf_url_tail_element = soup.find('div', {'id': '2b'})
        pdf_url_tail = pdf_url_tail_element.a.get('href')
        pdf_url = pdf_url_head + pdf_url_tail
        yield scrapy.Request(pdf_url, callback= self.parse_pdf_data, errback=self.handle_error,
                             cb_kwargs={'SPIDER_POC_JLR_PDF_ITEM': SPIDER_POC_JLR_PDF_ITEM})
        
#---------------獲取頁面資料---------------# 
    def get_page_data(self, soup, SPIDER_POC_JLR_PDF_ITEM):
        column_item_ls = soup.select('.list-group-item span')
        columns_name_ls = ["DECISION_NAME", "LEGAL_RELATIONSHIP", "JUDGMENT_LEVEL", "TYPE_OF_CASE", "TRIAL_COURT", 
                        "APPLICATION_OF_PRECEDENT", "CORRECTIONS", "INFORMATION_ABOUT_THE_CASE", "TOTAL_NUMBER_OF_VOTES_VOTED_AS_THE_SOURCE_OF_CASE_LAW_DEVELOPMENT"]
        for column_item, columns_name in zip(column_item_ls, columns_name_ls):
            SPIDER_POC_JLR_PDF_ITEM[columns_name] = column_item.text
        regex = r"\d{2}\.\d{2}\.\d{4}"
        SPIDER_POC_JLR_PDF_ITEM["UPDATE_DATE"] = re.findall(regex, SPIDER_POC_JLR_PDF_ITEM["DECISION_NAME"])[0]
        return SPIDER_POC_JLR_PDF_ITEM
        

#---------------處理PDF Data---------------#
    def parse_pdf_data(self, response, SPIDER_POC_JLR_PDF_ITEM):
        pdf_file = io.BytesIO(response.body)
        text = ''
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = text + str(page) + page.extract_text()
        SPIDER_POC_JLR_PDF_ITEM["PDF_TEXT"] = text
        yield SPIDER_POC_JLR_PDF_ITEM

#---------------處理例外---------------#
    def handle_error(self, failure):
        logging.error(f'Request failed: {failure}' )