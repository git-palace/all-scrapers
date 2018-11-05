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

from dbmanager import *

class tripadvisor(scrapy.Spider):

	name = 'tripadvisor'

	domain = ''

	history = []

	countryURLs = []


	def __init__(self):

		if checkDBConnection() and isTableExisting('ATTRACTIONS_TABLE_FROM_TRIPADVISOR') and isTableExisting('COUNTRY_CODE_TO_COUNTRY_NAME_TABLE'):
			lines = []
			
			with open('require/CountryURLs.csv', 'r') as f:
				lines = f.readlines()

			for line in lines:
				line = self.validate(line)

				if 'http' in line:
					self.countryURLs.append({'country': line.split(',http')[0],'url' : 'http'+line.split(',http')[-1]})


	
	def start_requests(self):

		for countryURL in self.countryURLs:

			print countryURL['url']

			url = 'https://www.tripadvisor.com/'

			yield scrapy.Request(url=countryURL['url'], callback=self.parse_country_page)

			break


	def parse_country_page(self, response):

		pass


	def parse(self, response):

		with open('res.txt', 'wb') as f:

			f.write(response.body)

		pdb.set_trace()


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