
import io
import pdfplumber
import scrapy
import logging
from bs4 import BeautifulSoup
from Spider_POC_JLR.items import SpiderPocJlrPdfItem
from datetime import datetime
import os
from google.cloud import bigquery

today = datetime.today().date()
today = today.strftime("%m%d")

class JudgementInfoSpider(scrapy.Spider):
    bq_table_name = f'judgement_info_{today}'
    name = "jlr_judgement_info"

#---------------開始Request---------------# 
    def start_requests(self):
        self.SPIDER_POC_JLR_PDF_ITEM = SpiderPocJlrPdfItem()
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = "spider-poc-gcp-key.json"
        client = bigquery.Client(project="spider-poc")
        query = """
            SELECT JLR_LINK
            FROM `spider-poc.spider_poc_jlr.judgement_link_0324`
            LIMIT 1000
        """
        query_job = client.query(query)
        all_links = [row[0] for row in query_job.result()]
        print(len(all_links))
        for link in all_links:  
            # logging.info(f'url is {link}')
            yield scrapy.Request(link, callback= self.parse_pdf_link, errback=self.handle_error) 

#---------------處理資料---------------# 
    def parse_pdf_link(self, response):
        #處理頁面資訊
        soup = BeautifulSoup(response.body, "html.parser")
        column_item_ls = soup.select('.list-group-item span')
        columns_name_ls = ["DECISION_NAME", "LEGAL_RELATIONSHIP", "JUDGMENT_LEVEL", "TYPE_OF_CASE", "TRIAL_COURT", 
                        "APPLICATION_OF_PRECEDENT", "CORRECTIONS", "INFORMATION_ABOUT_THE_CASE", "TOTAL_NUMBER_OF_VOTES_VOTED_AS_THE_SOURCE_OF_CASE_LAW_DEVELOPMENT"]
        #找到頁面中的PDF連結
        pdf_url_head = "https://congbobanan.toaan.gov.vn/"
        for column_item, columns_name in zip(column_item_ls, columns_name_ls):
            self.SPIDER_POC_JLR_PDF_ITEM[columns_name] = column_item.text
        pdf_url_tail_element = soup.find('div', {'id': '2b'})
        pdf_url_tail = pdf_url_tail_element.a.get('href')
        pdf_url = pdf_url_head + pdf_url_tail
        yield scrapy.Request(pdf_url, callback= self.parse_pdf_data, errback=self.handle_error)

#---------------處理PDF Data---------------#
    def parse_pdf_data(self, response):
        pdf_file = io.BytesIO(response.body)
        text = ''
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = text + str(page) + page.extract_text()
        self.SPIDER_POC_JLR_PDF_ITEM["PDF_TEXT"] = text
        yield self.SPIDER_POC_JLR_PDF_ITEM

#---------------處理例外---------------#
    def handle_error(self, failure):
        logging.error(f'Request failed: {failure}' )