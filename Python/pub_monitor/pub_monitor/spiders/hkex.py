# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import json
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
from urllib.parse import urljoin

class HkexSpider(scrapy.Spider):
    name = 'hkex'
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("HKEX", "duration"))
   
    allowed_domains = ['www1.hkexnews.hk']
    start_urls = [f"https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId=-1&documentType=-1&fromDate={(datetime.today()-timedelta(days=duration)).strftime('%Y%m%d')}&toDate={datetime.today().strftime('%Y%m%d')}&title=&searchType=1&t1code=40000&t2Gcode=-2&t2code=40100&rowRange=5000&lang=E", f"https://www1.hkexnews.hk/search/titleSearchServlet.do?sortDir=0&sortByOptions=DateTime&category=0&market=SEHK&stockId=-1&documentType=-1&fromDate={(datetime.today()-timedelta(days=duration)).strftime('%Y%m%d')}&toDate={datetime.today().strftime('%Y%m%d')}&title=&searchType=1&t1code=40000&t2Gcode=-2&t2code=40400&rowRange=5000&lang=E"]

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/hkex.xlsx")
    search_keys = list(df.SEARCH_KEY)

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        json_data = json.loads(response.text)
        data = eval(json_data['result'])
        for row in data:
            HkexSpider.items['publication_date'] = date = datetime.strptime(row['DATE_TIME'], "%d/%m/%Y %H:%M")
            stock_code = row['STOCK_CODE'].split('<br/>')
            HkexSpider.items['doc_name'] = title = row['TITLE'] + (" (CSR)" if "t2code=40400" in response.url else "")
            HkexSpider.items['doc_link'] = urljoin("https://www1.hkexnews.hk", row['FILE_LINK']) + ("+AR" if "t2code=40100" in response.url else "+CSR")
            if any(int(x) in HkexSpider.search_keys for x in stock_code):
                input = HkexSpider.df[HkexSpider.df['SEARCH_KEY'].isin(stock_code)]
                HkexSpider.items['ukey'] = input['U_KEY'].values[0]
                HkexSpider.items['mkey'] = input['M_KEY'].values[0]
                HkexSpider.items['company_name'] = input['Company Name'].values[0]
                HkexSpider.items['company_id'] = input['Company ID'].values[0]
                HkexSpider.items['domicile'] = input['DOMICILE'].values[0]
                HkexSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                HkexSpider.items['update_date'] = datetime.now()
                HkexSpider.items['year'] = date.year
                HkexSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                yield HkexSpider.items

