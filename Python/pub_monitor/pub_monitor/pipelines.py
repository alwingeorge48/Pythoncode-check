# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

from scrapy.exporters import CsvItemExporter
from configparser import ConfigParser
import os, pathlib

class PubMonitorPipeline(object):
    def __init__(self):
        configs = ConfigParser()
        path = pathlib.Path(os.path.realpath(__file__))
        configs.read(path.parent.parent/'config.ini')
        self.file = open(f"{configs.get('APP', 'output_dir')}/booksdata.csv", 'a+b')
        self.exporter = CsvItemExporter(self.file)
        self.exporter.start_exporting()

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
