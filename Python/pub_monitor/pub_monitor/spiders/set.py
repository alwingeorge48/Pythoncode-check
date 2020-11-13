# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import re
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem

class SetSpider(scrapy.Spider):
    name = 'set'
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')

    allowed_domains = ['www.set.or.th']

    def start_requests(self):
        df = pd.read_excel(f"{SetSpider.configs.get('APP', 'input_dir')}/set.xlsx")
        df = df[df['SEARCH_KEY'].notna()]
        for index, row in df.iterrows():
            url = f"https://www.set.or.th/set/companyprofile.do?symbol={row['SEARCH_KEY']}&ssoPageId=4&language=en&country=US"
            yield scrapy.Request(url, meta=row.to_dict())

    def validation(self, year):
        return True if (year == datetime.today().year) else False

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.body, 'lxml')
        elements = soup.find('table').find_all('tr')[0].find('td').find_all('div', recursive=False)[5]
        year = [i.text for i in elements.find_all('a')]
        link = [i.attrs['href'] for i in elements.find_all('a')]
        dates = re.findall(r"[0-9]+/[0-9]+/[0-9]+", elements.text)
        dates = [datetime.strptime(i, "%d/%m/%Y") for i in dates]
        for i in zip(year, link, dates):
            SetSpider.items['publication_date'] = i[2]
            SetSpider.items['doc_link'] = i[1]
            SetSpider.items['year'] = year = i[2].year
            SetSpider.items['doc_name'] = "Annual Report"
            SetSpider.items['mkey'] = response.meta['M_KEY']
            SetSpider.items['ukey'] = response.meta['U_KEY']
            SetSpider.items['company_id'] = response.meta['Company ID']
            SetSpider.items['company_name'] = response.meta['Company Name']
            SetSpider.items['domicile'] = response.meta['DOMICILE']
            SetSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            SetSpider.items['update_date'] = datetime.now()
            SetSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            if self.validation(year):
                yield SetSpider.items

