# from __future__ import unicode_literals
import scrapy
import json
import os
import scrapy
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
from selenium.webdriver.support.select import Select
from lxml import etree
from lxml import html
import time
import pdb


class todo(scrapy.Spider):
	name = 'ves-service'
	history = []
	output = []
	domain = 'https://www.vesservices.com/secure/loginform.aspx'

	def __init__(self):
		options = webdriver.ChromeOptions()
		options.add_argument('headless')
		self.driver = webdriver.Chrome('./chromedriver.exe', chrome_options=options)
		self.driver.maximize_window()

		pass

	
	def start_requests(self):
		yield scrapy.Request(url=self.domain, callback=self.parse)


	def parse(self, response):

		self.driver.get(self.domain)
		
		Select(self.driver.find_element_by_id('LoginType')).select_by_value('2')
		self.driver.find_element_by_id('LoginName').send_keys('username')
		self.driver.find_element_by_id('Pwd').send_keys('password')
		self.driver.find_element_by_id('bLogin').click()

		time.sleep(1)

		self.driver.get('https://www.vesservices.com/Secure/va/vareview.aspx?ControlNumber=0')

		source = self.driver.page_source.encode("utf8")
		tree = etree.HTML(source)

		rows = tree.xpath('//table[@class="gridViewCaseList"]//tr')

		for row in rows:
			if not len(row.xpath('./td')):
				continue

			js_code = row.xpath('./td[1]/a/@href')[0]
			ex_date = row.xpath('./td[last()]/text()')[0]
			vba = '' if len(row.xpath("./td")) is not 3 else row.xpath('./td[2]/text()')[0]


			self.driver.execute_script(js_code.replace('javascript:', ''))

			source = self.driver.page_source.encode('utf8')
			tree = etree.HTML(source)

			item = dict()

			item['Name'] = self.get_text(tree, '//span[@id="ctl00_mainCopy_tbname"]/text()')
			item['VBA/VHA'] = vba
			item['Exam Date'] = ex_date
			item['Date of Birth'] = self.get_text(tree, '//span[@id="ctl00_mainCopy_tbdob"]/text()')
			item['VES Case'] = self.get_text(tree, '//span[@id="ctl00_mainCopy_tbmescase"]/text()')
			item['Email'] = self.get_text(tree, '//span[@id="ctl00_mainCopy_tbemail"]/text()')
			item['File Number'] = self.get_text(tree, '//span[@id="ctl00_mainCopy_tbssn"]/text()')
			item['Ex Worksheets'] = self.get_text(tree, '//table[@id="ctl00_mainCopy_GridView6"]/tbody/tr/td[1]/text()')

			yield item


	def get_text(self, source, selector):
		try:
			return '\n'.join(source.xpath(selector)) if len(source.xpath(selector)) > 1 else source.xpath(selector)[0]
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