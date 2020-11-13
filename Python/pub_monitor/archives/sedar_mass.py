# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import json
import logging
from configparser import ConfigParser
import os, pathlib
import sys
sys.path.append(r"/home/ubuntu/publication_monitor/pub_monitor/pub_monitor")
from items import PubMonitorItem
from fuzzywuzzy import fuzz
from scrapy_splash import SplashRequest

class SedarMassSpider(scrapy.Spider):
    name = 'sedar_mass'
    items = PubMonitorItem()
    allowed_domains = ['www.sedar.com']
    # start_urls = ['https://www.sedar.com/new_docs/new_annual_reports_en.htm']
    custom_settings = {'ROBOTSTXT_OBEY': False}

    def start_requests(self):
        sedar_list = pd.read_excel('/home/ubuntu/publication_monitor/pub_monitor/Book1.xlsx')
        for index, row in sedar_list[:1].iterrows():
            yield SplashRequest(f"https://www.sedar.com/DisplayCompanyDocuments.do?lang=EN&issuerNo={int(row['SEARCH_KEY2']):08}", meta={'company_id':row['Company ID'], 'company_name':row['Company Name'], 'domicile':row['DOMICILE'], 'trgr':row['TRIGGER_DOC'], 't_publication_date':row['T_PUBL_DATE']}, callback=self.parse)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        print(response.text)
        for row in soup.find_all('table')[1].find('tbody').find_all('tr')[2:]:
            date = row.find_all('td', recursive=False)[1].text.strip()
            SedarMassSpider.items['publication_date'] = date = datetime.strptime(date, "%b %d %Y")
            SedarMassSpider.items['doc_name'] = row.find_all('td', recursive=False)[3].text.strip()
            SedarMassSpider.items['doc_link'] = f"https://www.sedar.com/GetFile.do?lang=EN{row.find_all('td', recursive=False)[3].find('a').attrs['title']}"
            SedarMassSpider.items['ukey'] = None
            SedarMassSpider.items['mkey'] = None
            SedarMassSpider.items['update_date'] = datetime.now()
            SedarMassSpider.items['company_id'] = response.meta['company_id']
            SedarMassSpider.items['company_name'] = respsonse.meta['company_name']
            SedarMassSpider.items['domicile'] = response.meta['domicile']
            SedarMassSpider.items['trgr'] = response.meta['trgr']
            SedarMassSpider.items['t_publication_date'] = response.meta['t_publication_date']
            SedarMassSpider.items['year'] = date.year
            yield SedarMassSpider.items
