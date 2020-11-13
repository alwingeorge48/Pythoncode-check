# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
from urllib.parse import urljoin
import json

class CninfoSpider(scrapy.Spider):    
    name = 'cninfo_ar'
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("CNINFO", "duration"))
    CSR_keywords = ";".join(configs.get("CNINFO", "CSR_keywords").split(', '))

    # allowed_domains = ['http://www.cninfo.com.cn/']

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/cninfo.xlsx")
    df = df[~df['SEARCH_KEY'].isna()]
    df['SEARCH_KEY'] = df['SEARCH_KEY'].astype(int)
    search_keys = list(df.SEARCH_KEY)
    total_stock_dict = {}
    input_stock_str = ""

    with open(f"{configs.get('APP', 'misc_dir')}/cninfo_stockList.json") as fp:
        for i in json.load(fp)['stockList']:
            total_stock_dict[i['code']] = i['orgId']

    for count, row in df.iterrows():
        temp = f"{row['SEARCH_KEY']:06d}"
        input_stock_str = f"{input_stock_str}{temp},{total_stock_dict.get(temp)};"

    payload = { 'pageNum': '',
                'pageSize': '30',
                'column': 'szse',
                'tabName': 'fulltext',
                'stock': input_stock_str,
                'category': '',
                'searchkey': '',
                'seDate': f"{(date.today()-timedelta(days=duration)).strftime('%Y-%m-%d')}~{date.today().strftime('%Y-%m-%d')}",
                'sortName': 'time',
                'sortType': 'desc',
                'isHLtitle': 'true' }
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    
    def start_requests(self):
        CninfoSpider.payload['pageNum'] = '1'
        CninfoSpider.payload['category'] = 'category_ndbg_szsh'
        yield scrapy.FormRequest(CninfoSpider.url, callback=self.parse, formdata=CninfoSpider.payload)

    def parse(self, response):
        try:
            self.crawler.stats.set_value("spider_name", self.name)
            data = json.loads(response.text)
            data = data['announcements']
            for row in data:
                stock_code = int(row['secCode'].lstrip('0'))
                if stock_code in CninfoSpider.search_keys:
                    CninfoSpider.items['doc_name'] = row['announcementTitle'].replace('<em>', '').replace('</em>', '')
                    CninfoSpider.items['doc_link'] = urljoin("http://static.cninfo.com.cn/", row['adjunctUrl'])
                    input = CninfoSpider.df[CninfoSpider.df['SEARCH_KEY']==stock_code]
                    CninfoSpider.items['ukey'] = input['U_KEY'].values[0]
                    CninfoSpider.items['mkey'] = input['M_KEY'].values[0]
                    CninfoSpider.items['company_id'] = input['Company ID'].values[0]
                    CninfoSpider.items['company_name'] = input['Company Name'].values[0]
                    CninfoSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                    CninfoSpider.items['domicile'] = input['DOMICILE'].values[0]
                    CninfoSpider.items['update_date'] = datetime.now()
                    CninfoSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                    CninfoSpider.items['publication_date'] = date = datetime.fromtimestamp(int(row['announcementTime'])/1000)
                    CninfoSpider.items['year'] = date.year
                    yield CninfoSpider.items
            if len(data) == 30:
                next_page = response.urljoin(response.url)
                CninfoSpider.payload['pageNum'] = str(int(CninfoSpider.payload['pageNum'])+1)
                yield scrapy.FormRequest(next_page, callback=self.parse, formdata=CninfoSpider.payload)
        except Exception:
            pass
