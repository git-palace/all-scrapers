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

	name = 'todo'

	domain = ''

	history = []


	def __init__(self):

		pass

	
	def start_requests(self):

		url  = ''

		yield scrapy.Request(url=url, callback=self.parse) 


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