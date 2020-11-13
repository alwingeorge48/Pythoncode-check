# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, date, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
import json
from urllib.parse import urljoin

class CninfoMassSpider(scrapy.Spider):
    name = 'cninfo_mass'
    allowed_domains = ['http://www.cninfo.com.cn/']
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("CNINFO", "duration"))
    AR_keywords = configs.get("CNINFO", "AR_keywords").split(', ')
    CSR_keywords = configs.get("CNINFO", "CSR_keywords").split(', ')

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/cninfo.xlsx")

    payload = {'stock': '',
        'tabName': 'fulltext',
        'pageSize': '30',
        'pageNum': '1',
        'column': '',
        'category': 'category_ndbg_szsh;',
        'plate': '',
        'seDate': '',
        'searchkey': '',
        'secid': '',
        'sortName': 'time',
        'sortType': 'desc',
        'isHLtitle': 'true'}
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"

    def start_requests(self):
        with open(f"{CninfoMassSpider.configs.get('APP', 'misc_dir')}/cninfo_stockList.json", 'r') as fp:
            stock_list = json.load(fp)
        stock_list = stock_list['stockList']
        for count, row in CninfoMassSpider.df.iterrows():
            try:
                stock_org_id = [(i['orgId'], i['code']) for i in stock_list if i['code'] == f"{row['SEARCH_KEY']:06d}"][0]
                CninfoMassSpider.payload['stock'] = f"{int(stock_org_id[1]):06d},{stock_org_id[0]}"
                CninfoMassSpider.payload['seDate'] = f"{(date.today()-timedelta(days=CninfoMassSpider.duration)).strftime('%Y-%m-%d')}~{date.today().strftime('%Y-%m-%d')}"
                yield scrapy.FormRequest(CninfoMassSpider.url, callback=self.parse, formdata=CninfoMassSpider.payload, meta=row.to_dict())
            except:
                print(f"************{row['SEARCH_KEY']}:Not found****************")
        for count, row in CninfoMassSpider.df[CninfoMassSpider.df['TRIGGER_DOC'] == 'CSR'].iterrows():
            try:
                stock_org_id = [(i['orgId'], i['code']) for i in stock_list if i['code'] == f"{row['SEARCH_KEY']:06d}"][0]
                CninfoMassSpider.payload['stock'] = f"{int(stock_org_id[1]):06d},{stock_org_id[0]}"
                CninfoMassSpider.payload['category'] = 'category_rcjy_szsh;'
                CninfoMassSpider.payload['seDate'] = f"{(date.today()-timedelta(days=CninfoMassSpider.duration)).strftime('%Y-%m-%d')}~{date.today().strftime('%Y-%m-%d')}"
                yield scrapy.FormRequest(CninfoMassSpider.url, callback=self.parse, formdata=CninfoMassSpider.payload, meta=row.to_dict())
            except:
                print(f"************{row['SEARCH_KEY']}:Not found****************")

    def validation(self, title):
        CninfoMassSpider.AR_keywords.extend(CninfoMassSpider.CSR_keywords)
        if any([key.lower() in title.lower() for key in CninfoMassSpider.AR_keywords]):
            return True

    def parse(self, response):
        json_data = json.loads(response.text)
        data = json_data['announcements']
        for row in data:
            CninfoMassSpider.items['doc_name'] = title =  row['announcementTitle']
            CninfoMassSpider.items['doc_link'] = urljoin("http://static.cninfo.com.cn/", row['adjunctUrl'])
            CninfoMassSpider.items['ukey'] = response.meta['U_KEY']
            CninfoMassSpider.items['mkey'] = response.meta['M_KEY']
            CninfoMassSpider.items['company_id'] = response.meta['Company ID']
            CninfoMassSpider.items['company_name'] = response.meta['Company Name']
            CninfoMassSpider.items['trgr'] = response.meta['TRIGGER_DOC']
            CninfoMassSpider.items['domicile'] = response.meta['DOMICILE']
            CninfoMassSpider.items['update_date'] = datetime.now()
            CninfoMassSpider.items['t_publication_date'] = response.meta['T_PUBL_DATE']
            CninfoMassSpider.items['publication_date'] = date = datetime.fromtimestamp(int(row['announcementTime'])/1000)
            CninfoMassSpider.items['year'] = date.year
            if self.validation(title):
                yield CninfoMassSpider.items
