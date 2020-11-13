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

class BseAnnSpider(scrapy.Spider):
    name = 'bse-ann'
    items = PubMonitorItem()
    allowed_domains = ['api.bseindia.com']

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("BSE", "duration"))
    AR_keywords = configs.get("BSE", "AR_keywords").split(', ')

    start_urls = ["https://api.bseindia.com/BseIndiaAPI/api/AnnGetData/w?strCat=-1&strPrevDate={0}&strScrip=&strSearch=P&strToDate={0}&strType=C".format((datetime.today()-timedelta(days=i)).strftime('%Y%m%d')) for i in range(duration)]

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/bse.xlsx")
    search_keys = list(df.SEARCH_KEY)

    def validation(self, title):
        if any([key.lower() in title.lower() for key in BseAnnSpider.AR_keywords]):
            return True

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        json_data = json.loads(response.text)
        data = json_data['Table']
        for row in data:
            BseAnnSpider.items['publication_date'] = date = datetime.strptime(row['NEWS_DT'].split('.')[0], "%Y-%m-%dT%H:%M:%S")
            stock_code = row['SCRIP_CD']
            BseAnnSpider.items['doc_name'] = title = row['NEWSSUB']
            BseAnnSpider.items['doc_link'] = urljoin('https://www.bseindia.com/xml-data/corpfiling/AttachLive/', row['ATTACHMENTNAME'])
            if stock_code in BseAnnSpider.search_keys:
                input = BseAnnSpider.df[BseAnnSpider.df['SEARCH_KEY']==stock_code]
                BseAnnSpider.items['ukey'] = input['U_KEY'].values[0]
                BseAnnSpider.items['mkey'] = input['M_KEY'].values[0]
                BseAnnSpider.items['company_name'] = input['Company Name'].values[0]
                BseAnnSpider.items['company_id'] = input['Company ID'].values[0]
                BseAnnSpider.items['domicile'] = input['DOMICILE'].values[0]
                BseAnnSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                BseAnnSpider.items['update_date'] = datetime.now()
                BseAnnSpider.items['year'] = date.year
                BseAnnSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                if self.validation(title):
                    yield BseAnnSpider.items
