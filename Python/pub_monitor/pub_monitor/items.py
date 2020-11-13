# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class PubMonitorItem(scrapy.Item):
    # define the fields for your item here like: 
    mkey = scrapy.Field()
    company_id = scrapy.Field()
    company_name = scrapy.Field()
    domicile = scrapy.Field()
    trgr = scrapy.Field()
    update_date = scrapy.Field()
    publication_date = scrapy.Field()
    doc_name = scrapy.Field()
    doc_link = scrapy.Field()
    ukey = scrapy.Field()
    year = scrapy.Field()
    t_publication_date = scrapy.Field()
