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
import urllib

class SgxSpider(scrapy.Spider):
    custom_settings = {'ROBOTSTXT_OBEY': False, 'USER_AGENT': 'Mozilla/5.0', 'DOWNLOAD_DELAY': 1}
    name = 'sgx'
    items = PubMonitorItem()
    # allowed_domains = ['www.sgx.com']

    configs = ConfigParser()
    path = pathlib.Path(os.path.realpath(__file__))
    configs.read(path.parent.parent.parent/'config.ini')
    duration = int(configs.get("SGX", "duration"))

    df = pd.read_excel(f"{configs.get('APP', 'input_dir')}/sgx.xlsx")
    search_keys = list(df.SEARCH_KEY)

    def url_inc(url, param, increment):
        parsed = urllib.parse.urlparse(url)
        d = dict(urllib.parse.parse_qsl(parsed.query, keep_blank_values=True))
        d[param] = str(int(d[param])+increment)
        p = parsed._replace(query=urllib.parse.urlencode(d))
        return urllib.parse.urlunparse(p)

    def cipher(validator_text):
        validator_text = validator_text.replace('\\', '')
        ciphered_validator_text = ""
        for ch in validator_text:
            if 97 <= ord(ch.lower()) < 110:
                    ciphered_validator_text += chr(ord(ch)+13)
            elif 110 <= ord(ch.lower()) <= 122:
                    ciphered_validator_text += chr(ord(ch)-13)
            else:
                    ciphered_validator_text+=str(ch)
        return ciphered_validator_text

    def start_requests(self):
        validator_text_url = 'https://api2.sgx.com/content-api/?queryId=900099aa7731cbb5e15e6e84bc83ff18072b4ba1:we_chat_qr_validator'
        yield scrapy.Request(validator_text_url, callback=self.parse)

    def parse(self, response):
        validator_text = json.loads(response.text)['data']['qrValidator'].replace('\\', '')
        SgxSpider.ciphered_validator_text = SgxSpider.cipher(validator_text)

        url = f"https://api.sgx.com/announcements/v1.1/?periodstart={(datetime.today()-timedelta(days=SgxSpider.duration)).strftime('%Y%m%d')}_160000&periodend={datetime.today().strftime('%Y%m%d')}_155959&cat=ANNC&sub=ANNC30&pagestart=0&pagesize=250"
        yield scrapy.Request(url, headers={'authorizationtoken': SgxSpider.ciphered_validator_text}, callback=self.further_parse1)

    def further_parse1(self, response):
        self.crawler.stats.set_value("spider_name", self.name)
        json_data = json.loads(response.text)
        data = json_data['data']
        for row in data:
            date = datetime.strptime(row['submission_date'], "%Y%m%d")
            stock_code = "fuck off"
            if row['issuers'] is not None:
                stock_code = row['issuers'][0]['stock_code']
            path = row['url']
            if stock_code in SgxSpider.search_keys:
                url = response.urljoin(path)
                yield scrapy.Request(url, callback=self.further_parse2, meta={'stock_code':stock_code, 'publication_date':date})
            if len(data) >= 250:
                next_page = response.urljoin(SgxSpider.url_inc(response.url, 'pagestart', 1))
                yield scrapy.Request(next_page, headers={'authorizationtoken': SgxSpider.ciphered_validator_text}, callback=self.further_parse1)

    def further_parse2(self, response):
        soup = BeautifulSoup(response.text, 'html.parser')
        SgxSpider.items['publication_date'] = response.meta['publication_date']
        SgxSpider.items['doc_link'] = final_path = urljoin('https://links.sgx.com/', soup.find_all('div')[-2].find('a').attrs['href'])
        SgxSpider.items['doc_name'] = final_path.split('/')[-1].split('.')[0].replace('%20', ' ')
        input = SgxSpider.df[SgxSpider.df['SEARCH_KEY']==response.meta['stock_code']]
        SgxSpider.items['ukey'] = input['U_KEY'].values[0]
        SgxSpider.items['mkey'] = input['M_KEY'].values[0]
        SgxSpider.items['company_name'] = input['Company Name'].values[0]
        SgxSpider.items['company_id'] = input['Company ID'].values[0]
        SgxSpider.items['domicile'] = input['DOMICILE'].values[0]
        SgxSpider.items['trgr'] = input['TRIGGER_DOC'].values[0]
        SgxSpider.items['update_date'] = datetime.now()
        SgxSpider.items['year'] = response.meta['publication_date'].year
        SgxSpider.items['t_publication_date'] = input['T_PUBL_DATE'].values[0]
        yield SgxSpider.items
