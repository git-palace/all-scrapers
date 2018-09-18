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

		with open('No Email Address.csv', 'rb') as csv_file:

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
		# yield scrapy.Request(url='https://www.gowillhart.com/', callback=self.parse, meta={'business_name': 'Go Will Hart', 'website': 'www.gowillhart.com'})



	def start_business_emails(self, response):

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

			text_arr = response.xpath('//body//text()').extract()

			email = ''

			for text in text_arr:

				email = self.check_email(text)

				if email:

					break

			if email:

				item['email'] = email

			yield item

		else:

			yield item


	def check_email(self, text):

		match = re.search(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", self.validate(text))

		if match:

			return match.group(0)

		return False

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