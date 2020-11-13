
# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
import urllib
from urllib.parse import urljoin

class EdinetSpider(scrapy.Spider):
    name = 'edinet'
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    AR_keywords = configs.get('EDINET', 'AR_keywords').split(', ')

    custom_settings = {'USER_AGENT': 'Mozilla/5.0'}

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/edinet.xlsx")
    df = df.loc[df['M_KEY']=='XJPEDINET', :]
    search_keys = list(df.SEARCH_KEY)

    start_urls = ["https://disclosure.edinet-fsa.go.jp/E01EW/BLMainController.jsp?uji.verb=W1E63013CXP001002ActionE&uji.bean=ee.bean.parent.EECommonSearchBean&TID=W1E63013&PID=W1E63013&SESSIONKEY=1587934648313&lgKbn=1&pkbn=0&skbn=1&dskb=&askb=&dflg=0&iflg=0&cal=2&mul=&fls=on&oth=on&mon=&yer=&pfs=2&row=100&idx=0&str=&kbn=1&flg=&syoruiKanriNo="]

    def url_inc(url, param, increment):
        parsed = urllib.parse.urlparse(url)
        d = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        d[param] = str(int(d[param])+increment)
        p = parsed._replace(query=urllib.parse.urlencode(d))
        return urllib.parse.urlunparse(p)

    def validation(self, title):
        if any([key.lower() in title.lower() for key in EdinetSpider.AR_keywords]):
            return True

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        table = soup.find('table', {'class': 'resultTable table_cellspacing_1 table_border_1 mb_6'}).find_all('tr', recursive=False)
        for count, row in enumerate(table):
            if count!= 0:
                elements = row.find_all('td', recursive=False)
                date = elements[0].text.strip()
                EdinetSpider.items['publication_date'] = date = datetime.strptime(date, "%Y.%m.%d %H:%M")
                extra_report = elements[4].text.strip()
                EdinetSpider.items['doc_name'] = title = f"{elements[1].text.strip()} {extra_report}"
                code = elements[2].text.split('/')[0].strip()
                fund = elements[3].text.strip()
                EdinetSpider.items['doc_link'] = link = f"https://disclosure.edinet-fsa.go.jp/{elements[5].find('a').attrs['href']}"[-8:]
                if code in EdinetSpider.search_keys:
                    input = EdinetSpider.df[EdinetSpider.df['SEARCH_KEY']==code]
                    EdinetSpider.items['ukey'] = input['U_KEY'].values[0]
                    EdinetSpider.items['company_id'] = input['Company ID'].values[0]
                    EdinetSpider.items['company_name'] = input['Company Name'].values[0]
                    EdinetSpider.items['mkey'] = input['M_KEY'].values[0]
                    EdinetSpider.items['domicile'] = input['DOMICILE'].values[0]
                    EdinetSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                    EdinetSpider.items['update_date'] = datetime.now()
                    EdinetSpider.items['year'] = date.year
                    EdinetSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                    if self.validation(title):
                        yield EdinetSpider.items
        if len(table) >= 101:
            next_page = response.urljoin(EdinetSpider.url_inc(response.url, 'idx', 100))
            yield scrapy.Request(next_page, callback=self.parse)

