# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from lxml import etree

from lxml import html

import pdb

import csv



class todo(scrapy.Spider):

	name = 'business-url-list'

	domain = 'yelp.com'

	history = []

	business_list = []


	def __init__(self):

		with open('center_result.csv', 'rb') as csv_file:

			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:

				item = {
					'business_name': row['business_name'],
					'detail_link': row['detail_link']
				}
				
				self.business_list.append(item)

		pass

	
	def start_requests(self):

		for business in self.business_list:

			yield scrapy.Request(url=business['detail_link'], callback=self.parse, meta={'business_name': business['business_name']})


	def parse(self, response):

		try:

			item = ChainItem()

			item['business_name'] = response.meta['business_name']

			item['website'] = self.validate(response.xpath('//span[contains(@class, "biz-website")]/a/text()').extract_first())

			yield item

		except:

			pass


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp