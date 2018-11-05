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
from datetime import datetime, date, timedelta


class Magnum4d(scrapy.Spider):
	name = 'magnum4d'
	filename = 'magnum4d.txt'
	history = []


	def __init__(self):
		if os.path.exists(self.filename):
			with open(self.filename, 'r') as f:
				self.history = f.readlines()


	def url_generator(self, date_from, date_to):
		url = 'https://webservices.magnum4d.my/results/past/between-dates/%02d-%02d-%04d/%02d-%02d-%04d/9' % (date_from.day, date_from.month, date_from.year, date_to.day, date_to.month, date_to.year)

		return url

	
	def start_requests(self):

		yield scrapy.Request(url='https://www.magnum4d.my/en', callback=self.parse_past_results)


	def parse_past_results(self, response):
		if 'date_to' not in response.meta:
			date_to = date.today()
		else:
			date_to = response.meta['date_to']

		date_from = date_to - timedelta(days=10)

		url  = self.url_generator(date_from, date_to)

		try:
			results = json.loads(response.body)

			if 'PastResultsRange' in results and 'PastResults' in results['PastResultsRange']:
				self.write_past_result(results['PastResultsRange']['PastResults'])

		except:
			pass


		if date_from.year >= 1980:
			yield scrapy.Request(url=url, callback=self.parse_past_results, meta={'date_to': date_from - timedelta(days=1)}, dont_filter = True)


	def write_past_result(self, data_list):
		keys = ['DrawDate', 'FirstPrize', 'SecondPrize', 'ThirdPrize']
		keys += map(lambda x: 'Special%s' % (x), range(1, 11))
		keys += map(lambda x: 'Console%s' % (x), range(1, 11))


		for data in data_list:
			txt = ''

			for key in keys:
				if key == 'DrawDate':
					draw_date = datetime.strptime(data[key], '%d/%m/%Y')
					txt += '%04d%02d%02d, ' % (draw_date.year, draw_date.month, draw_date.day)
				elif key == 'FirstPrize':
					txt += '1: %s, ' % (data[key])
				elif key == 'SecondPrize':
					txt += '2: %s, ' % (data[key])
				elif key == 'ThirdPrize':
					txt += '3: %s, ' % (data[key])
				elif 'Special' in key:
					txt += 'SP: %s, ' % (data[key])
				elif 'Console' in key:
					txt += 'CN: %s, ' % (data[key])

			txt += '\n'

			if txt not in self.history:
				self.history.append(txt)

				with open(self.filename, 'a+') as f:
					f.write(txt)
					print txt