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

class LondonSpider(scrapy.Spider):
    name = 'london'
    allowed_domains = ['www.londonstockexchange.com']
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("LONDON", "duration"))

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/london.xlsx")
    search_keys = list(df.SEARCH_KEY)

    start_urls = [f"https://www.londonstockexchange.com/news?tab=news-explorer&size=500&headlinetypes=1,2&headlines=98&period=custom&beforedate={datetime.today().strftime('%Y%m%d')}&afterdate={(datetime.today()-timedelta(days=duration)).strftime('%Y%m%d')}"]

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find('div', {'id': 'news-table-results'}).find('table').find('tbody').find_all('tr'):
            elements = row.find_all('td')
            LondonSpider.items['doc_name'] = elements[0].find('a').text
            LondonSpider.items['doc_link'] = urljoin("https://www.londonstockexchange.com/", elements[0].find('a').attrs['href'])
            LondonSpider.items['publication_date'] = date = datetime.strptime(elements[2].text.strip(), "%d.%m.%y")
            stock_code = elements[0].text.split(' - ')[1]
            if stock_code in LondonSpider.search_keys:
                input = LondonSpider.df[LondonSpider.df['SEARCH_KEY']==stock_code]
                LondonSpider.items['ukey'] = input['U_KEY'].values[0]
                LondonSpider.items['mkey'] = input['M_KEY'].values[0]
                LondonSpider.items['company_name'] = input['Company Name'].values[0]
                LondonSpider.items['company_id'] = input['Company ID'].values[0]
                LondonSpider.items['domicile'] = input['DOMICILE'].values[0]
                LondonSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                LondonSpider.items['update_date'] = datetime.now()
                LondonSpider.items['year'] = date.year
                LondonSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                yield LondonSpider.items
