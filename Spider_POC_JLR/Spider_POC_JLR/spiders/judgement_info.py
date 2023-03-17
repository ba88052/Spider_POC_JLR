
import io
import pdfplumber
import time
import sys
import json
import scrapy
import logging
from tqdm import tqdm
from bs4 import BeautifulSoup
from Spider_POC_JLR.items import SpiderPocJlrItem
from datetime import datetime, timedelta
from scrapy_selenium import SeleniumRequest
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


#---------------設定year的年份，可調整start_date和end_date----------------#
start_date = '01/01/2023'
today = datetime.today().date()
two_days_ago = today - timedelta(days=2)
two_days_ago_str = two_days_ago.strftime('%d/%m/%Y')
end_date = two_days_ago_str

class JudgementInfoSpider(scrapy.Spider):
    name = "jlr_judgement_info"

#---------------開啟Selenium----------------#
    def start_requests(self):
        self.SPIDER_POC_JLR_ITEM = SpiderPocJlrItem()
        yield SeleniumRequest(
            url='https://congbobanan.toaan.gov.vn/0tat1cvn/ban-an-quyet-dinh',
            wait_until=EC.visibility_of_element_located((By.CSS_SELECTOR, "button.sp-prompt-btn.sp-disallow-btn")),
            callback=self.parse,
            wait_time = 30
        )
        

#---------------連線到頁面，並處理彈出視窗---------------#
    def start_driver(self, driver, wait):
        #處理彈出視窗
        dnotallow_notifications_btn = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, "button.sp-prompt-btn.sp-disallow-btn")))
        dnotallow_notifications_btn.click()
        #處理第一次進入頁面時需選擇角色的視窗
        choice_role = driver.find_element(By.ID, "ctl00_Feedback_Home_Radio_STYLE_1")
        choice_role.click()
        submit_role = driver.find_element(By.ID, "ctl00_Feedback_Home_cmdSave_Regis")
        submit_role.click()
        return True

#---------------輸入日期開始搜尋---------------#
    def start_search(self, driver, wait):
        #輸入日期
        time.sleep(2)
        search_date_to = driver.find_element(By.ID, "ctl00_Content_home_Public_ctl00_Rad_DATE_TO_top")
        search_date_to.clear()
        search_date_to.send_keys(end_date)
        time.sleep(2)
        search_date_from = driver.find_element(By.ID, "ctl00_Content_home_Public_ctl00_Rad_DATE_FROM_top")
        search_date_from.clear()
        search_date_from.send_keys(start_date)
        # search_date_from.send_keys('03/03/2023')
        time.sleep(2)
        #按下搜尋
        submit_search = driver.find_element(By.ID, "ctl00_Content_home_Public_ctl00_cmd_search_banner")
        submit_search.click()

#---------------進入網頁後的主控制----------------#
    def parse(self, response):
        all_links = []
        driver = response.meta['driver']
        wait = WebDriverWait(driver, 30)
        #設置最大重試次數
        max_retries = 5
        retry_count = 0
        get_cookie = False
        #若超過最大重試次數則跳ERROR
        while retry_count < max_retries:
            try:
                #處理第一次進入網頁時會挑出要求通知的問題，用try是因為不確定是否每次都會要求通知
                if not get_cookie:
                    try:
                        get_cookie = self.start_driver(driver, wait)
                    except:
                        pass
                #開始搜尋
                self.start_search(driver, wait)
                date_to = wait.until(EC.visibility_of_element_located((By.ID, "ctl00_Content_home_Public_ctl00_Rad_DATE_TO")))
                date_to_value = date_to.get_attribute("value")
                date_from = driver.find_element(By.ID, "ctl00_Content_home_Public_ctl00_Rad_DATE_FROM")
                date_from_value = date_from.get_attribute("value")
            except:
                retry_count += 1
                logging.warning(f"Error occurred: Search Wrong Retry Times#{retry_count}")
                time.sleep(1)
                driver.refresh()
                continue
            
            #如果進入搜尋頁面後的日期與設定日期不符，則重試
            if date_to_value != two_days_ago_str or date_from_value != start_date:
                retry_count += 1
                logging.warning(f"Error occurred: Date Wrong Retry Times#{retry_count}")
                driver.refresh()
                continue
            else:
                break
        #若超過最大重試次數則跳ERROR
        if retry_count == max_retries:
            logging.error(f"Error occurred: Retry Enough Times")
            driver.quit()
            sys.exit()
        else:
            #total_pages 總頁數
            total_pages = wait.until(EC.visibility_of_element_located((By.ID, "ctl00_Content_home_Public_ctl00_LbShowtotal"))).text
            print("Total Pages:", total_pages)
            for page in tqdm(range(1, int(total_pages)+1)):
                #獲得當前頁面所有Link
                one_page_links = driver.find_elements(By.CSS_SELECTOR, 'a.echo_id_pub')
                one_page_links_li = [link.get_attribute('href') for link in one_page_links]
                all_links += one_page_links_li
                next_page = driver.find_element(By.ID, "ctl00_Content_home_Public_ctl00_cmdnext")
                try:
                    #切換到下一頁，如果不行，則視同最後一頁
                    next_page.click()
                    WebDriverWait(driver, 10).until(EC.text_to_be_present_in_element((By.CSS_SELECTOR, 'select.page_option_pub option[selected]'), str(page)))
                except:
                    continue
            print("Get Link Success!!")
            driver.quit()

            with open('list.json', 'w') as file:
                json.dump(all_links, file)
            for link in all_links:
                yield scrapy.Request(link, callback= self.parse_pdf_link, errback=self.handle_error) 
    
#---------------找到頁面中的PDF連結---------------#    
    def parse_pdf_link(self, response):        
        pdf_url_head = "https://congbobanan.toaan.gov.vn/"
        soup = BeautifulSoup(response.body, "html.parser")
        column_item_ls = soup.select('.list-group-item span')
        columns_name_ls = ["DECISION_NAME", "LEGAL_RELATIONSHIP", "JUDGMENT_LEVEL", "TYPE_OF_CASE", "TRIAL_COURT", "APPLICATION_OF_PRECEDENT", "CORRECTIONS", "INFORMATION_ABOUT_THE_CASE"]
        for column_item, columns_name in zip(column_item_ls, columns_name_ls):
            self.SPIDER_POC_JLR_ITEM[columns_name] = column_item.text
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
        self.SPIDER_POC_JLR_ITEM["PDF_TEXT"] = text
        yield self.SPIDER_POC_JLR_ITEM

    def handle_error(self, failure):
        logging.error(f'Request failed: {failure}' )
