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


class houzz(scrapy.Spider):

	name = 'houzz'

	history = []

	output = []

	domain = 'https://www.houzz.com'

	def __init__(self):

		# self.driver = webdriver.Chrome('./chromedriver.exe')

		pass

	
	def start_requests(self):
		urls = [
			# 'https://www.houzz.com/professionals/searchDirectory?topicId=11788&query=Landscape+Architects+%26+Landscape+Designers&location=Ontario&distance=100&sort=5',
			# 'https://www.houzz.com/professionals/searchDirectory?topicId=11795&query=Swimming+Pool+Builders&location=Ontario&distance=100&sort=5',
			# 'https://www.houzz.com/professionals/searchDirectory?topicId=11812&query=Landscape+Contractors&location=Ontario&distance=100&sort=5',
			# 'https://www.houzz.com/professionals/searchDirectory?topicId=11824&query=Stone%2C+Pavers+%26+Concrete&location=Ontario&distance=100&sort=5',
			'https://www.houzz.com/professionals/searchDirectory?topicId=11823&query=Home+Builders&location=Ontario&distance=100&sort=5'
		]

		for url in urls:
			yield scrapy.Request(url=url, callback=self.parse_page)


	def parse_page(self, response):
		for detail_link in response.xpath('//li[@class="hz-pro-search-results__item"]//a[@itemprop="url"]/@href').extract():
			yield scrapy.Request(url=detail_link, callback=self.parse_detail_page)

		if len(response.xpath('//div[@class="hz-card mbl hz-track-me"]//a[@class="hz-pagination-link hz-pagination-link--next"]/@href')):
			url = response.xpath('//div[@class="hz-card mbl hz-track-me"]//a[@class="hz-pagination-link hz-pagination-link--next"]/@href').extract_first()
			url = url.replace('www.houzz.com', '').replace('https://', '')

			yield scrapy.Request(url=self.domain+url, callback=self.parse_page)


	def parse_detail_page(self, response):
		# pdb.set_trace()
		try:
			data = response.body.split('<script id="hz-ctx" type="application/json">')[1].split('</script>')[0]
			data = json.loads(data)['data']['stores']['data']

			item = dict()

			userData = data['UserProfileStore']['data']['user']
			item['Company name'] = userData['displayName']
			
			contactName = userData['contactName'].split()
			item['Contact first name'] = self.get_first_value(contactName)
			item['Contact last name'] = ' '.join(contactName)

			tree = etree.HTML(userData['professional']['seoFormattedAddress'])
			item['Unit & street (incl. suite)'] = self.get_first_value(tree.xpath('//span[@itemprop="streetAddress"]/text()'))
			item['City'] = self.get_first_value(tree.xpath('//span[@itemprop="addressLocality"]/a/text()'))
			item['Province'] = self.get_first_value(tree.xpath('//span[@itemprop="addressRegion"]/text()'))
			item['Postal code'] = self.get_first_value(tree.xpath('//span[@itemprop="postalCode"]/text()'))
			item['Contact phone #'] = userData['professional']['formattedPhone']

			try:
				text = data['PageStore']['data']['pageDescriptionFooter']
				text = text.replace('<runnable type="application/ld+json">', '').replace('</runnable>', '')
				url = json.loads(self.eliminate_space(text))[0]['url']
				url = url.replace('http://', '').replace('https://', '')

				item['Website'] = 'http://' + url if url else ''
			except:
				item['Website'] = ''

			item['# of reviews'] = userData['professional']['numReviews']
			
			reviewRating = userData['professional']['reviewRating']
			reviewRating = reviewRating / 10 + (1 if reviewRating % 10 > 7 else (0.5 if reviewRating % 10 > 3 else 0))
			item['Rating (stars)'] = reviewRating

			yield item
		except:
			try:
				data = response.body.split('<script type="application/ld+json">')[1].split('</script>')[0]
				data = json.loads(data)[0]

				item = dict()

				item['Company name'] = data['name']

				try:
					contactName = response.xpath('//i[contains(@class, "icon-person")]/following-sibling::div/text()').extract_first().split()
					item['Contact first name'] = self.get_first_value(contactName)
					item['Contact last name'] = ' '.join(contactName)
				except:
					item['Contact first name'] = ''
					item['Contact last name'] = ''

				try:
					item['Unit & street (incl. suite)'] = data['address']['streetAddress']
					item['City'] = data['address']['addressLocality']
					item['Province'] = data['address']['addressRegion']
					item['Postal code'] = data['address']['postalCode']
				except:
					item['Unit & street (incl. suite)'] = ''
					item['City'] = ''
					item['Province'] = ''
					item['Postal code'] = ''

				try:
					item['Contact phone #'] = data['telephone']
				except:
					item['Contact phone #'] = ''
				
				try:
					url = response.xpath('//a[@compid="Profile_Website"]/@href').extract_first()
					url = url.replace('http://', '').replace('https://', '')
					item['Website'] = 'http://' + url if url else ''
				except:
					item['Website'] = ''

				try:
					item['# of reviews'] = data['aggregateRating']['reviewCount']
				except:
					item['# of reviews'] = 0
			
				try:
					item['Rating (stars)'] = data['aggregateRating']['ratingValue']
				except:
					item['Rating (stars)'] = 0

				yield item
			except:
				with open('failed-urls.txt', 'a') as f:
					f.write(response.url + '\n')


	def get_first_value(self, item):
		return item.pop(0) if len(item) else ''

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

	    return ''.join(tmp)