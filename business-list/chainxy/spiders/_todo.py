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


class todo(scrapy.Spider):

	name = 'business-list'

	domain = 'yelp.com'

	history = []

	headers = {
		'authorization': 'Bearer 0NFnf2i_frOPM0v000Aq4r_3s3y5vavJ2wsMPWGzD2ZnIHjEL_ebOu1GY3BoV2n0oMtZMf7ZIOGGftN2whFtAgnuJAc2e36vKK6bqw-CUYfpayPSW9EBJXwxtd6SW3Yx'
	}

	# center (34.0863012, -117.7698408)
	# bottom left (30.38567, -97.7226)
	latitude = 30.38567

	longitude = -97.7226

	radius = 40000

	limit = 50

	def __init__(self):

		with open('categories.json', 'r') as f:
			self.categories = json.load(f)

	def start_requests(self):

		for category in self.categories:

			org_url = 'https://api.yelp.com/v3/businesses/search?categories=%s&latitude=%s&longitude=%s&radius=%s&limit=%s' % (category['alias'], self.latitude, self.longitude, self.radius, self.limit)

			url = '%s&offset=%s' % (org_url, 0)

			yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={'org_url': org_url, 'offset': 0})

		pass

	def parse(self, response):

		item = ChainItem()

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
			
						item['business_name'] = business['name']

						item['phone'] = business['display_phone']

						item['lat'] = business['coordinates']['latitude']

						item['lng'] = business['coordinates']['longitude']

						item['detail_link'] = business['url']

						self.history.append(business)

						yield item

				except:

					pass

			if total > 50:

				url = '%s&offset=%s' % (response.meta['org_url'], response.meta['offset'] + 50)

				yield scrapy.Request(url=url, callback=self.parse, headers=self.headers, meta={'org_url': response.meta['org_url'], 'offset': response.meta['offset'] + 50, 'total': total - 50})

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
