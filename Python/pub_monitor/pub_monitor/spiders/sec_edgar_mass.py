# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
import re
import html

class SecEdgarMassSpider(scrapy.Spider):
    name = 'sec-edgar-mass'
    allowed_domains = ['www.sec.gov']
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    forms = configs.get("SEC", "forms").split(', ')
    duration = int(configs.get("SEC", "duration"))

    def start_requests(self):
        df = pd.read_excel(f"{SecEdgarMassSpider.configs.get('APP', 'input_dir')}/sec.xlsx")
        df = df[df['SEARCH_KEY2'].notna()]
        for i, row in df.tail(50).iterrows():
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK={int(row['SEARCH_KEY2'])}&owner=exclude&count=100&datea={(datetime.today()-timedelta(days=SecEdgarMassSpider.duration)).strftime('%Y%m%d')}&output=atom"
            yield scrapy.Request(url, callback=self.parse, meta=row.to_dict())

    def validation(self, title):
        if any([key.lower() in title.lower() for key in SecEdgarMassSpider.forms]):
            return True

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'lxml')
        for element in soup.find_all('entry'):
            d = re.split('</b> | <b>', html.unescape(element.find('summary').text))[2]
            SecEdgarMassSpider.items['publication_date'] = date = datetime.strptime(d, "%Y-%m-%d")
            SecEdgarMassSpider.items['doc_name'] = title = element.find('title').text.split(' - ')[0]
            SecEdgarMassSpider.items['doc_link'] = element.find('link').attrs['href']
            SecEdgarMassSpider.items['ukey'] = response.meta['U_KEY']
            SecEdgarMassSpider.items['company_id'] = response.meta['Company ID']
            SecEdgarMassSpider.items['company_name'] = response.meta['Company Name']
            SecEdgarMassSpider.items['mkey'] = response.meta['M_KEY']
            SecEdgarMassSpider.items['domicile'] = response.meta['DOMICILE']
            SecEdgarMassSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            SecEdgarMassSpider.items['update_date'] = datetime.now()
            SecEdgarMassSpider.items['year'] = date.year
            SecEdgarMassSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            if self.validation(title):
                yield SecEdgarMassSpider.items
