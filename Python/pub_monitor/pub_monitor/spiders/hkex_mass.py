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

class HkexMassSpider(scrapy.Spider):
    name = 'hkex_mass'
    allowed_domains = ['www1.hkexnews.hk']
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("HKEX", "duration"))

    payload = {'lang': 'EN',
        'category': '0',
        'market': 'SEHK',
        'searchType': '1',
        'documentType': '-1',
        't1code': '40000',
        't2Gcode': '-2',
        't2code': '',
        'stockId': '',
        'from': (datetime.today()-timedelta(days=duration)).strftime("%Y%m%d"),
        'to': datetime.today().strftime("%Y%m%d"),
        'MB-Daterange': '0'}

    url = "https://www1.hkexnews.hk/search/titlesearch.xhtml?lang=en"

    def start_requests(self):
        df = pd.read_excel(f"{HkexMassSpider.configs.get('APP', 'input_dir')}/hkex.xlsx")
        df = df[df['SEARCH_KEY2'].notna()]
        for index, row in df.iterrows():
            HkexMassSpider.payload['t2code'] = '40100'
            HkexMassSpider.payload['stockId'] = str(row['SEARCH_KEY2'])
            yield scrapy.FormRequest(HkexMassSpider.url, callback=self.parse, formdata=HkexMassSpider.payload, meta=row.to_dict())
        for index, row in df[df['TRIGGER_DOC'] == 'CSR'].iterrows():
            HkexMassSpider.payload['t2code'] = '40400'
            HkexMassSpider.payload['stockId'] = str(row['SEARCH_KEY2'])
            yield scrapy.FormRequest(HkexMassSpider.url, callback=self.parse, formdata=HkexMassSpider.payload, meta=row.to_dict())

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find('table').find('tbody').find_all('tr'):
            element = row.find_all('td')
            HkexMassSpider.items['publication_date'] = date = datetime.strptime(element[0].contents[2], "%d/%m/%Y %H:%M")
            HkexMassSpider.items['doc_name'] = title = element[3].find('a').text.strip()
            HkexMassSpider.items['doc_link'] = f"https://www1.hkexnews.hk/{element[3].find('a').attrs['href']}"
            HkexMassSpider.items['ukey'] = response.meta['U_KEY']
            HkexMassSpider.items['company_id'] = response.meta['Company ID']
            HkexMassSpider.items['company_name'] = response.meta['Company Name']
            HkexMassSpider.items['mkey'] = response.meta['M_KEY']
            HkexMassSpider.items['domicile'] = response.meta['DOMICILE']
            HkexMassSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            HkexMassSpider.items['update_date'] = datetime.now()
            HkexMassSpider.items['year'] = date.year
            HkexMassSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            yield HkexMassSpider.items
