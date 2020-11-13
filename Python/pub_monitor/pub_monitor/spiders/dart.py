# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
from urllib.parse import urljoin

class DartSpider(scrapy.Spider):
    name = 'dart'
    allowed_domains = ['http://dart.fss.or.kr/']
    items = PubMonitorItem()
    custom_settings = {'ROBOTSTXT_OBEY': False, 'USER_AGENT': 'Mozilla/5.0', 'DOWNLOAD_DELAY': 2, 'CONCURRENT_REQUESTS': 1}

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("DART", "duration"))

    payload = {'currentPage': '1',
        'maxResults': '15',
        'maxLinks': '10',
        'sort': 'date',
        'series': 'desc',
        'textCrpCik': '',
        'textCrpNm': '064960',
        'finalReport': 'recent',
        'startDate': (datetime.today()-timedelta(days=duration)).strftime('%Y%m%d'),
        'endDate': datetime.today().strftime('%Y%m%d'),
        'publicType': 'A001'}
    url = "http://dart.fss.or.kr/dsab001/search.ax"

    def start_requests(self):
        df = pd.read_excel(f"{DartSpider.configs.get('APP', 'input_dir')}/korea.xlsx")
        for index, row in df[df['SEARCH_KEY'].notna()].iterrows():
            DartSpider.payload['textCrpNm'] = f"{int(row['SEARCH_KEY']):06d}"
            DartSpider.payload['stockId'] = str(row['SEARCH_KEY2'])
            yield scrapy.FormRequest(DartSpider.url, callback=self.parse, formdata=DartSpider.payload, meta=row.to_dict())

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find('table').find('tbody').find_all('tr'):
            element = row.find_all('td')
            DartSpider.items['doc_name'] = element[2].text.strip().replace('\r', '').replace('\n', '').replace('\t', '')
            DartSpider.items['publication_date'] = date = datetime.strptime(element[4].text, "%Y.%m.%d")
            DartSpider.items['doc_link'] = urljoin("http://dart.fss.or.kr/", element[2].find('a').attrs['href'])
            DartSpider.items['ukey'] = response.meta['U_KEY']
            DartSpider.items['company_id'] = response.meta['Company ID']
            DartSpider.items['company_name'] = response.meta['Company Name']
            DartSpider.items['mkey'] = response.meta['M_KEY']
            DartSpider.items['domicile'] = response.meta['DOMICILE']
            DartSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            DartSpider.items['update_date'] = datetime.now()
            DartSpider.items['year'] = date.year
            DartSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            yield DartSpider.items
