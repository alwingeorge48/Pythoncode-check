# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
import re
import html
import urllib

class SecEdgarSpider(scrapy.Spider):
    name = 'sec-edgar'
    allowed_domains = ['www.sec.gov']
    items = PubMonitorItem()

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    forms = configs.get("SEC", "forms").split(', ')

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/sec.xlsx")
    search_keys = list(df.SEARCH_KEY2)

    def start_requests(self):
        for i in SecEdgarSpider.forms:
            url = f"https://www.sec.gov/cgi-bin/browse-edgar?action=getcurrent&CIK=&type={i}&company=&dateb=&owner=include&start=0&count=100&output=atom"
            yield scrapy.Request(url)

    def url_inc(url, param, increment):
        parsed = urllib.parse.urlparse(url)
        d = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        d[param] = str(int(d[param])+increment)
        p = parsed._replace(query=urllib.parse.urlencode(d))
        return urllib.parse.urlunparse(p)

    def parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'lxml')
        for element in soup.find_all('entry'):
            d = re.split('</b> | <b>', html.unescape(element.find('summary').text))[2]
            SecEdgarSpider.items['publication_date'] = date = datetime.strptime(d, "%Y-%m-%d")
            s = element.find('title').text
            cik = int(s[s.find("(")+1:s.find(")")])
            SecEdgarSpider.items['doc_name'] = element.find('title').text.split(' - ')[0]
            SecEdgarSpider.items['doc_link'] = element.find('link').attrs['href']
            if cik in SecEdgarSpider.search_keys:
                input = SecEdgarSpider.df[SecEdgarSpider.df['SEARCH_KEY2']==cik]
                SecEdgarSpider.items['ukey'] = input['U_KEY'].values[0]
                SecEdgarSpider.items['company_id'] = input['Company ID'].values[0]
                SecEdgarSpider.items['company_name'] = input['Company Name'].values[0]
                SecEdgarSpider.items['mkey'] = input['M_KEY'].values[0]
                SecEdgarSpider.items['domicile'] = input['DOMICILE'].values[0]
                SecEdgarSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
                SecEdgarSpider.items['update_date'] = datetime.now()
                SecEdgarSpider.items['year'] = date.year
                SecEdgarSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
                yield SecEdgarSpider.items
            if len(soup.find_all('entry')) >= 100:
                next_page = response.urljoin(SecEdgarSpider.url_inc(response.url, 'start', 100))
                yield scrapy.Request(next_page, callback=self.parse)
