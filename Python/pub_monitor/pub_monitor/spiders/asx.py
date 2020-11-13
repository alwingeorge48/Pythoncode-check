# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
import json
from ..items import PubMonitorItem
from urllib.parse import urljoin

class AsxSpider(scrapy.Spider):
    name = 'asx'
    items = PubMonitorItem()
    allowed_domains = ['www.asx.com']

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    
    duration = int(configs.get("ASX", "duration"))
    start_urls = [f"https://asx.api.markitdigital.com/asx-research/1.0/markets/announcements?announcementTypes[]=annual+report&dateStart={(datetime.today()-timedelta(days=duration)).strftime('%Y-%m-%d')}&dateEnd={datetime.today().strftime('%Y-%m-%d')}&page=0&itemsPerPage=5000&summaryCountsDate={datetime.today().strftime('%Y-%m-%d')}"]

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/asx.xlsx")
    search_keys = list(df.SEARCH_KEY)

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        json_data = json.loads(response.text)
        data = json_data['data']['items']
        for row in data:
            AsxSpider.items['publication_date'] = date = datetime.strptime(row['date'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
            AsxSpider.items['doc_name'] = row['headline']
            AsxSpider.items['doc_link'] = urljoin('https://asx.api.markitdigital.com/asx-research/1.0/file/', row['documentKey'])
            if row['symbol'] in AsxSpider.search_keys:
                input = AsxSpider.df[AsxSpider.df['SEARCH_KEY']==row['symbol']]
                AsxSpider.items['ukey'] = input['U_KEY'].values[0]
                AsxSpider.items['company_id'] = input['Company ID'].values[0]
                AsxSpider.items['company_name'] = input['Company Name'].values[0]
                AsxSpider.items['mkey'] = input['M_KEY'].values[0]
                AsxSpider.items['domicile'] = input['DOMICILE'].values[0]
                AsxSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                AsxSpider.items['update_date'] = datetime.now()
                AsxSpider.items['year'] = date.year
                AsxSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                yield AsxSpider.items
