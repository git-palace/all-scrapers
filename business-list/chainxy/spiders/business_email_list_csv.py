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



class business_email_list_csv(scrapy.Spider):

	name = 'business-email-list-csv'

	domain = 'yelp.com'

	history = []

	business_list = []


	def __init__(self):

		with open('00_business-list_20180928.csv', 'rb') as csv_file:

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

						yield scrapy.Request(url=url, callback=self.parse, meta={'business_name': business['business_name'], 'website': url})

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

				contact_link = response.xpath('//a[contains(text(), "contact") or contains(text(), "Contact") or contains(text(), "CONTACT")]/@href').extract_first()

				if not contact_link:

					yield item

				else:

					if contact_link not in self.history:

						self.history.append(contact_link)

						url = '%s%s' % (response.meta['website'] if 'http' not in contact_link else '', contact_link)

						try:

							yield scrapy.Request(url=url, callback=self.parse, meta={'business_name': response.meta['business_name'], 'website': item['website']})

						except:

							pass
							
					else:

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