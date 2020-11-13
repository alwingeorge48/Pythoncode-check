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

class SedarSpider(scrapy.Spider):
    name = 'sedar'
    items = PubMonitorItem()
    allowed_domains = ['www.sedar.com']
    # start_urls = ['https://www.sedar.com/new_docs/new_annual_reports_en.htm']
    custom_settings = {'ROBOTSTXT_OBEY': False}

    def start_requests(self):
        url = "https://www.sedar.com/new_docs/new_annual_reports_en.htm"
        yield SplashRequest(url, callback=self.parse)
        # url = "https://www.sedar.com/new_docs/all_new_pc_filings_en.htm"
        # yield SplashRequest(url, callback=self.parse)

    def string_cleaner(self, s):
        s = s.replace(',', '').replace('.', '')
        noise_words = ('in', 'inc', 'ltd', 'co', 'corp', 'corporation', 'limited', 'ltee', 'limitee', 'trust', 'incorporated', 'company', 'in.', 'inc.', 'ltd.', 'co.', 'corp.', ',', 'cor', 'inc/c', 'a', 'the', 'c', 'lt', 'lt.', 'group', 'group.', 'groups', 'solution', 'solutions', 'financial')
        return ' '.join(w.lower().replace(',', '') for w in s.split() if w.lower() not in noise_words)

    def parse(self, response):
        print(response.text)
        matching_df = pd.DataFrame(columns=['company_name_website', 'company_name_filed', 'matching_score', 'mkey'])
        matching_count = 0
        soup = BeautifulSoup(response.text, 'html.parser')
        rows = soup.find_all('table')[1].find_all('tr', recursive=True)
        header = [0]
        for count, i in enumerate(rows):
            if (i.find('td', {'colspan':'5', 'valign':'TOP'})) is not None:
                print(i.text)
                header.append(count)
        header.append(len(rows)+1)
        df = pd.read_excel(r"/home/ubuntu/publication_monitor/pub_monitor/Book1.xlsx")
        companies = list(df['Company Name'])
        for count, i in enumerate(header[1:-1], start=1):
            for j in range(i+1, header[count+1]-1):
                company_name = rows[i].text.strip()
                date = rows[j].find_all('td', recursive=False)[1].text.strip()
                SedarSpider.items['publication_date'] = date  = datetime.strptime(date, "%b %d %Y")
                SedarSpider.items['doc_name'] = name =  rows[j].find_all('td', recursive=False)[3].text.strip()
                SedarSpider.items['doc_link'] = link = f"https://www.sedar.com/GetFile.do?lang=EN{rows[j].find_all('td', recursive=False)[3].find('a').attrs['title']}"
                ratios = []
                for company in companies:
                    ratios.append(fuzz.token_set_ratio(self.string_cleaner(company_name), self.string_cleaner(company)))
                # print("***"+companies[ratios.index(max(ratios))], max(ratios))
                df_row = df[df['Company Name']==companies[ratios.index(max(ratios))]]
                matching_df.loc[matching_count] = [company_name, df_row['Company Name'].iloc[0], max(ratios), 'SEDAR']
                matching_count +=1
                if (max(ratios)>=90):
                    SedarSpider.items['company_name'] = df_row['Company Name'].iloc[0]
                    SedarSpider.items['company_id'] = df_row['Company ID'].iloc[0]
                    SedarSpider.items['mkey'] = None
                    SedarSpider.items['trgr'] = df_row['TRIGGER_DOC'].iloc[0]
                    SedarSpider.items['ukey'] = None
                    SedarSpider.items['update_date'] = datetime.now()
                    SedarSpider.items['domicile'] = df_row['DOMICILE'].iloc[0]
                    SedarSpider.items['year'] = date.year
                    SedarSpider.items['t_publication_date'] = df_row['T_PUBL_DATE'].iloc[0]
                    yield SedarSpider.items
        matching_df.to_excel('/home/ubuntu/publication_monitor/pub_monitor/matching_name.xlsx', index=False)
