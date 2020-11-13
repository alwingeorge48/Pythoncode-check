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

class DartEnglishSpider(scrapy.Spider):
    name = 'dart_english'
    allowed_domains = ['http://englishdart.fss.or.kr']
    
    items = PubMonitorItem()
    custom_settings = {'ROBOTSTXT_OBEY': False, 'USER_AGENT': 'Mozilla/5.0', 'DOWNLOAD_DELAY': 2, 'CONCURRENT_REQUESTS': 1}

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("DART", "duration"))

    payload = {'currentPage' : '1',
        'maxResults': '',
        'maxLinks': '',
        'sort': '',
        'series': '',
        'textCrpCik': '',
        'textCrpNm': '002350',
        'startDate': (datetime.today()-timedelta(days=duration)).strftime('%Y%m%d'),
        'endDate': datetime.today().strftime('%Y%m%d'),
        'closingAccounts': ['0403', '0401']}
    url = "http://englishdart.fss.or.kr/dsbd002/search.ax"

    def start_requests(self):
        df = pd.read_excel(f"{DartEnglishSpider.configs.get('APP', 'input_dir')}/korea.xlsx")
        for index, row in df[df['SEARCH_KEY'].notna()].iterrows():
            DartEnglishSpider.payload['textCrpNm'] = f"{int(row['SEARCH_KEY']):06d}"
            yield scrapy.FormRequest(DartEnglishSpider.url, callback=self.parse, formdata=DartEnglishSpider.payload, meta=row.to_dict())

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find('table').find('tbody').find_all('tr'):
            element = row.find_all('td')
            doc_name = element[2].text.strip().replace('\r', '').replace('\n', '').replace('\t', '')
            DartEnglishSpider.items['doc_name'] = f"{'-'.join(element[4].text.strip().split()[:2])} {element[5].text.strip()} {element[6].text.strip()}"
            DartEnglishSpider.items['publication_date'] = date = datetime.strptime(element[1].text.strip(), "%Y.%m.%d")
            DartEnglishSpider.items['doc_link'] = urljoin("http://englishdart.fss.or.kr/", element[4].find('a').attrs['href'])
            DartEnglishSpider.items['ukey'] = response.meta['U_KEY']
            DartEnglishSpider.items['company_id'] = response.meta['Company ID']
            DartEnglishSpider.items['company_name'] = response.meta['Company Name']
            DartEnglishSpider.items['mkey'] = response.meta['M_KEY']
            DartEnglishSpider.items['domicile'] = response.meta['DOMICILE']
            DartEnglishSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            DartEnglishSpider.items['update_date'] = datetime.now()
            DartEnglishSpider.items['year'] = date.year
            DartEnglishSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            yield DartEnglishSpider.items
