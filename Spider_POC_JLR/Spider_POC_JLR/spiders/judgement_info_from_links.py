
import io
import pdfplumber
import json
import scrapy
import logging
from bs4 import BeautifulSoup
from Spider_POC_JLR.items import SpiderPocJlrItem



class JudgementInfoSpider(scrapy.Spider):
    name = "jlr_judgement_info_from_links"
    
    def start_requests(self):
        self.count_pdf_url = 0
        self.count_pdf_file = 0
        self.url =0
        self.pdf_link = []
        self.SPIDER_POC_JLR_ITEM = SpiderPocJlrItem()
        with open('list.json', 'r') as file:
            all_links = json.load(file)
        for link in all_links:
            # logging.info(f'url is {link}')
            yield scrapy.Request(link, callback= self.parse_pdf_link, errback=self.handle_error) 
            

#---------------找到頁面中的PDF連結---------------#    
    def parse_pdf_link(self, response):
        self.url += 1       
        pdf_url_head = "https://congbobanan.toaan.gov.vn/"
        soup = BeautifulSoup(response.body, "html.parser")
        column_item_ls = soup.select('.list-group-item span')
        columns_name_ls = ["DECISION_NAME", "LEGAL_RELATIONSHIP", "JUDGMENT_LEVEL", "TYPE_OF_CASE", "TRIAL_COURT", "APPLICATION_OF_PRECEDENT", "CORRECTIONS", "INFORMATION_ABOUT_THE_CASE"]
        for column_item, columns_name in zip(column_item_ls, columns_name_ls):
            self.SPIDER_POC_JLR_ITEM[columns_name] = column_item.text
        pdf_url_tail_element = soup.find('div', {'id': '2b'})
        pdf_url_tail = pdf_url_tail_element.a.get('href')
        pdf_url = pdf_url_head + pdf_url_tail
        self.pdf_link.append(pdf_url)
        # logging.info(f'pdf_url is {pdf_url}')
        self.count_pdf_url += 1
        yield scrapy.Request(pdf_url, callback= self.parse_pdf_data, errback=self.handle_error)
#---------------處理PDF Data---------------#    
    def parse_pdf_data(self, response):
        with open('pdf_url_list.json', 'w') as file:
                json.dump(self.pdf_link, file)
        pdf_file = io.BytesIO(response.body)
        text = ''
        with pdfplumber.open(pdf_file) as pdf:
            for page in pdf.pages:
                text = text + str(page) + page.extract_text()
        self.SPIDER_POC_JLR_ITEM["PDF_TEXT"] = text
        self.count_pdf_file += 1
        yield self.SPIDER_POC_JLR_ITEM
        logging.info(f"url = {self.url}, count_pdf_url = {self.count_pdf_url}, count_pdf_file = {self.count_pdf_file}")

    def handle_error(self, failure):
        logging.error(f'Request failed: {failure}' )