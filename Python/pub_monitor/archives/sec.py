
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
from time import time
import logging
from configparser import ConfigParser
import os, pathlib
import sys
sys.path.append(r"/home/ubuntu/publication_monitor/pub_monitor/pub_monitor")
from items import PubMonitorItem

class SecSpider(scrapy.Spider):
    name = 'sec'
    items = PubMonitorItem()
    custom_settings = {'ROBOTSTXT_OBEY':False}
    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    gap_days = int(configs.get('APP', 'gap_days'))

    logging.basicConfig(filename=configs.get('APP', 'log_file'), filemode='a', format='%(asctime)s:%(levelname)s:%(message)s')
    allowed_domains = ['sec.report']

    def start_requests(self):
        df = pd.read_excel(self.configs.get('APP', 'input_file'))
        for index, row in df.loc[df['M_KEY']=='XSEC', :][:5].iterrows():
            url = f"https://sec.report/Ticker/{row['SEARCH_KEY']}"
            yield scrapy.Request(url, meta={'ukey':row['U_KEY'], 'company_id':row['Company ID'], 'company_name':row['Company Name'], 'mkey':row['M_KEY'], 'domicile':row['DOMICILE'], 'trgr':row['TRIGGER_DOC']})

    def parse(self, response):
        soup = BeautifulSoup(response.body, 'lxml')
        for count, row in enumerate(soup.find_all('div', {"class":"panel-body"})[2].find_all('tr')):
            if count!= 0:
                elements = row.find_all('td')
                form = elements[0].text
                SecSpider.items['doc_link'] = link = f"https://sec.report/{elements[1].find('a').attrs['href']}"
                SecSpider.items['doc_name'] = title = f"{elements[1].find('a').text} ({form})"
                date = elements[1].find('small').text
                SecSpider.items['publication_date'] = date = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                SecSpider.items['company_id'] = response.meta['company_id']
                SecSpider.items['company_name'] = response.meta['company_name']
                SecSpider.items['mkey'] = response.meta['mkey']
                SecSpider.items['update_date'] = datetime.now()
                SecSpider.items['ukey'] = response.meta['ukey']
                SecSpider.items['domicile'] = reposnse.meta['domicile']
                SecSpider.items['trgr'] = resonse.meta['trgr']
                SecSpider.items['year'] = date.year
                yield SecSpider.items

