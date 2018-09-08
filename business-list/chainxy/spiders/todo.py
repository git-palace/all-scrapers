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

import re



class todo(scrapy.Spider):

	name = 'business-email-list'

	domain = 'yelp.com'

	history = []

	business_list = []


	def __init__(self):

		with open('center_result_websites.csv', 'rb') as csv_file:

			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:

				item = {
					'business_name': row['business_name'],
					'website': row['website']
				}
				
				self.business_list.append(item)

		pass

	
	def start_requests(self):

		yield scrapy.Request(url='https://yelp.com', callback=self.start_business_emails)



	def start_business_emails(self, response):

		pdb.set_trace()

		for business in self.business_list:

			url = ''

			item = ChainItem()

			item['business_name'] = business['business_name']

			try:

				if business['website']:

					if 'http' in business['website']:

						url = business['website']

					else:

						url = 'http://' + business['website']

						yield scrapy.Request(url=url, callback=self.parse, meta={'business_name': business['business_name'], 'website': business['website']})

				else:

					yield item

			except:

				yield item


	def parse(self, response):

		item = ChainItem()

		item['business_name'] = response.meta['business_name']

		item['website'] = response.meta['website']

		if (response.status == 200):

			email = self.validate(response.xpath('//a[contains(@href, "mailto")]/@href').extract_first())

			if email:

				item['email'] = email.split('?')[0]

			yield item

		else:

			yield item


	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t','').replace('\r', '').replace('mailto:', '').strip()

		except:

			pass


	def eliminate_space(self, items):

	    tmp = []

	    for item in items:

	        if self.validate(item) != '':

	            tmp.append(self.validate(item))

	    return tmp