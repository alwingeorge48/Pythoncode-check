# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem

class BseSpider(scrapy.Spider):
    name = 'bse'
    items = PubMonitorItem()
    allowed_domains = ['www.bseindia.com']

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')

    def start_requests(self):
        df = pd.read_excel(f"{BseSpider.configs.get('APP', 'input_dir')}/bse.xlsx")
        df = df[df['SEARCH_KEY'].notna()]
        for index, row in df.iterrows():
            url = f"https://api.bseindia.com/BseIndiaAPI/api/AnnualReport/w?scripcode={int(row['SEARCH_KEY'])}"
            yield scrapy.Request(url, meta=row.to_dict())

    def validation(self, year):
        return True if (year == datetime.today().year) else False

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        self.stock_code = response.request.url[-6:]
        json_data = json.loads(response.text)
        data = json_data['Table']
        for row in data:
            BseSpider.items['publication_date'] = date = datetime.strptime(row['dt_tm'], "%Y-%m-%dT%H:%M:%S")
            BseSpider.items['doc_link'] = path = f"https://www.bseindia.com/bseplus/AnnualReport/{self.stock_code}/{row['file_name']}"
            BseSpider.items['doc_name'] = "Annual Report"
            BseSpider.items['ukey'] = response.meta['U_KEY']
            BseSpider.items['company_id'] = response.meta['Company ID']
            BseSpider.items['company_name'] = response.meta['Company Name']
            BseSpider.items['mkey'] = response.meta['M_KEY']
            BseSpider.items['domicile'] = response.meta['DOMICILE']
            BseSpider.items['update_date'] = datetime.now()
            BseSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            BseSpider.items['year'] = year = int(date.year)
            BseSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            if self.validation(year):
                yield BseSpider.items

