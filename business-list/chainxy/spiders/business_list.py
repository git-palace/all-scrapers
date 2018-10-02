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


class business_list(scrapy.Spider):

	name = 'business-list'

	domain = 'yelp.com'

	history = []

	headers = {
		'authorization': 'Bearer OD8kvMGMthwtv3_d4mzUOzCg69JmOIlsT423nluPr1-Wms01bYZN-ZD1zGv2jqivwYkiQjo2eRqAz3RHci4J1wLOzi07pMZf4Gg_tyWG8ZNQ2kHEI4Z30I1tnqSuW3Yx'
	}

	latitude = 38.1166238

	longitude = -122.4171257

	radius = 40000

	limit = 50



	def __init__(self):

		with open('categories.json', 'r') as f:
			self.categories = json.load(f)



	def start_requests(self):

		yield scrapy.Request(url='https://www.yelp.com/', callback=self.search_businesses)



	def search_businesses(self, response):

		for category in self.categories:

			org_url = 'https://api.yelp.com/v3/businesses/search?categories=%s&latitude=%s&longitude=%s&radius=%s&limit=%s' % (category['alias'], self.latitude, self.longitude, self.radius, self.limit)

			url = '%s&offset=%s' % (org_url, 0)

			yield scrapy.Request(url=url, callback=self.parse_search_result, headers=self.headers, meta={'org_url': org_url, 'offset': 0})



	def parse_search_result(self, response):

		data = json.loads(response.body)

		total = 0

		if 'total' in response.meta:

			total = response.meta['total']

		else:

			total = data['total']


		if len(data['businesses']):

			for business in data['businesses']:

				try:

					if business not in self.history:
			
						self.history.append(business)

						item = ChainItem()

						item['business_name'] = business['name']

						item['lat'] = business['coordinates']['latitude']

						item['lng'] = business['coordinates']['longitude']

						yield scrapy.Request(url=business['url'], callback=self.parse_detail_page, meta={'item': item})

				except:

					pass

			if total > 50:

				url = '%s&offset=%s' % (response.meta['org_url'], response.meta['offset'] + 50)

				yield scrapy.Request(url=url, callback=self.parse_search_result, headers=self.headers, meta={'org_url': response.meta['org_url'], 'offset': response.meta['offset'] + 50, 'total': total - 50})




	def parse_detail_page(self, response):

		try:

			item = response.meta['item']

			item['website'] = self.validate(response.xpath('//span[contains(@class, "biz-website")]/a/text()').extract_first())

			if item['website']:

				yield item

		except:

			pass



	def validate(self, item):

		try:

			return item.replace('\n', '').replace('\t', '').replace('\r', '').strip()

		except:

			pass



	def eliminate_space(self, items):

		tmp = []

		for item in items:

			if self.validate(item) != '':

				tmp.append(self.validate(item))

		return tmp

