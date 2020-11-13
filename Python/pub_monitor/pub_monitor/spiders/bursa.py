# -*- coding: utf-8 -*-
import scrapy
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime, timedelta
import logging
from configparser import ConfigParser
import os, pathlib
from ..items import PubMonitorItem
import urllib
from urllib.parse import urljoin

class BursaSpider(scrapy.Spider):
    name = 'bursa'
    items = PubMonitorItem()
    #allowed_domains = ['www.bursamalaysia.com']

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("Bursa", "duration"))

    start_urls = [f'https://www.bursamalaysia.com/market_information/announcements/company_announcement?keyword=&cat=AR,ARCO&sub_type=&company=&mkt=&alph=&sec=&subsec=&dt_ht={(datetime.today()-timedelta(days=duration)).strftime("%d/%m/%Y")}&dt_lt={datetime.today().strftime("%d/%m/%Y")}&per_page=50&page=1']

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/bursa.xlsx")
    search_keys = list(df.SEARCH_KEY)

    def url_inc(url, param, increment):
        parsed = urllib.parse.urlparse(url)
        d = dict(urllib.parse.parse_qsl(parsed.query))
        d[param] = str(int(d[param])+increment)
        p = parsed._replace(query=urllib.parse.urlencode(d))
        return urllib.parse.urlunparse(p)

    def parse(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        for row in soup.find('table', {'id':'table-announcements'}).find('tbody').find_all('tr'):
            elements = row.find_all('td')
            date = datetime.strptime(elements[1].find_all('div')[1].text.strip(), "%d %b %Y")
            path = f"https://disclosure.bursamalaysia.com/FileAccess/viewHtml?e={elements[3].find('a').attrs['href'].split('=')[1]}"
            stock_code = int(elements[2].find('a').attrs['href'].split('=')[1])
            if stock_code in BursaSpider.search_keys:
                url = response.urljoin(path)
                yield scrapy.Request(url, callback=self.further_parse, meta={'stock_code':stock_code, 'publication_date':date})
        if len(soup.find('table', {'id':'table-announcements'}).find('tbody').find_all('tr')) == 50:
            next_page = response.urljoin(BursaSpider.url_inc(response.url, 'page', 1))
            yield scrapy.Request(next_page, callback=self.parse)

    def further_parse(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        soup = BeautifulSoup(response.text, 'html.parser')
        for file in soup.find_all('p', {'class':'att_download_pdf'}):
            input = BursaSpider.df[BursaSpider.df['SEARCH_KEY']==response.meta['stock_code']]
            BursaSpider.items['publication_date'] = response.meta['publication_date']
            BursaSpider.items['ukey'] = input['U_KEY'].values[0]
            BursaSpider.items['mkey'] = input['M_KEY'].values[0]
            BursaSpider.items['company_name'] = input['Company Name'].values[0]
            BursaSpider.items['company_id'] = input['Company ID'].values[0]
            BursaSpider.items['domicile'] = input['DOMICILE'].values[0]
            BursaSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
            BursaSpider.items['update_date'] = datetime.now()
            BursaSpider.items['year'] = response.meta['publication_date'].year
            BursaSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
            BursaSpider.items['doc_name'] = file.find('a').text.strip()
            BursaSpider.items['doc_link'] = urljoin("https://disclosure.bursamalaysia.com/", file.find('a').attrs['href'])
            yield BursaSpider.items
