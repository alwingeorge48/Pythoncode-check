# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
from dateutil.relativedelta import relativedelta

class TwseSpider(scrapy.Spider):
    custom_settings = {'ROBOTSTXT_OBEY': False, 'USER_AGENT': 'Mozilla/5.0', 'DOWNLOAD_DELAY': 6}
    name = 'twse'
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    AR_keywords = configs.get('TWSE', 'AR_keywords').split(', ')

    def start_requests(self):
        df = pd.read_excel(f"{TwseSpider.configs.get('APP', 'input_dir')}/twse.xlsx")
        for index, row in df.iterrows():
            url = f"https://doc.twse.com.tw/server-java/t57sb01?step=1&colorchg=1&co_id={row['SEARCH_KEY']}&year={(datetime.today()-relativedelta(years=1911)).year}&mtype=F&"
            yield scrapy.Request(url, meta=row.to_dict())

    def validation(self, title):
        if any([key.lower() in title.lower() for key in TwseSpider.AR_keywords]):
            return True

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.body, 'lxml')
        for count, row in enumerate(soup.find_all('table')[1].find_all('tr')):
            if count!=0:
                elements = row.find_all('td')
                TwseSpider.items['doc_name'] = title = elements[5].text
                TwseSpider.items['doc_link'] = link = elements[7].find('a').attrs['href'].replace('"', '')
                TwseSpider.items['publication_date'] = date = datetime.strptime(f"0{elements[9].text}", "%Y/%m/%d %H:%M:%S") + relativedelta(years=1911)
                TwseSpider.items['ukey'] = response.meta['U_KEY']
                TwseSpider.items['mkey'] = response.meta['M_KEY']
                TwseSpider.items['company_id'] = response.meta['Company ID']
                TwseSpider.items['company_name'] = response.meta['Company Name']
                TwseSpider.items['domicile'] = response.meta['DOMICILE']
                TwseSpider.items['trgr'] = response.meta['TRIGGER_DOC']
                TwseSpider.items['update_date'] = datetime.now()
                TwseSpider.items['year'] = date.year
                TwseSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
                if self.validation(title):
                    yield TwseSpider.items
