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

import datetime



class todo(scrapy.Spider):

	name = 'booking'

	domain = ''

	count = {}

	history = []

	locations = {}


	def __init__(self):

		with open('us-cities.csv', 'rb') as csv_file:

			csv_reader = csv.DictReader(csv_file)

			for row in csv_reader:

				for state, city in row.items():

					if state not in self.locations:
					
						self.locations[state] = []

						self.count[state] = {}

					self.count[state][city] = 0

					self.locations[state].append(city)



	def start_requests(self):

		for state, cities in self.locations.items():

			for city in cities:

				url  = 'https://www.booking.com/city/us/%s.html' % (city.lower().replace(' ', '-'))

				yield scrapy.Request(url=url, callback=self.parse_city_page, meta={'state': state, 'city': city})



	def parse_city_page(self, response):

		if response.status == 200:

			more_url = 'https://www.booking.com/searchresults.html'

			key_list = response.xpath('//form[@id="frm"]//input/@name').extract()

			start_date = datetime.datetime.today() + datetime.timedelta(days=7)

			end_date = start_date + datetime.timedelta(days=2)

			for key in key_list:

				if key == 'checkin_month':

					value = start_date.month

				elif key == 'checkin_monthday':

					value = start_date.day

				elif key == 'checkin_year':

					value = start_date.year

				elif key == 'checkout_month':

					value = end_date.month

				elif key == 'checkout_monthday':

					value = end_date.day

				elif key == 'checkout_year':

					value = end_date.year

				else:

					value = self.validate(response.xpath('//form[@id="frm"]//input[@name="%s"]/@value' % (key)).extract_first())

				more_url = ('%s%s%s=%s') % (more_url, '?' if key_list.index(key) == 0 else '&', key, value)

			yield scrapy.Request(url=more_url, callback=self.parse_all_hotels_in_city, meta={'state': response.meta['state'], 'city': response.meta['city']})



	def parse_all_hotels_in_city(self, response):

		hotel_tag_list = response.xpath('//div[@id="hotellist_inner"]/div[contains(@class, "sr_item")]')

		state = response.meta['state']

		city = response.meta['city']

		for hotel_tag in hotel_tag_list:

			try:

				title = self.validate(hotel_tag.xpath('.//span[contains(@class, "sr-hotel__name")]/text()').extract_first())

				price = self.validate(hotel_tag.xpath('.//strong[contains(@class, "price")]/b/text()').extract_first())

				detail_link = self.validate(hotel_tag.xpath('.//a[contains(@class, "hotel_name_link")]/@href').extract_first())

				if detail_link:

					if self.count[state][city] > 50:

						break

					detail_link = 'https://www.booking.com%s' % (detail_link)

					yield scrapy.Request(url=detail_link, callback=self.parse_detail_page_link, meta={'title': title, 'price': price, 'state': response.meta['state'], 'city': response.meta['city']}, dont_filter=True )

			except:

				pass

		next_url = response.xpath('//div[contains(@class, "results-paging")]//a[contains(@class, "paging-next")]/@href').extract_first()

		if next_url:

			next_url = 'https://www.booking.com%s' % (next_url)

			yield scrapy.Request(url=next_url, callback=self.parse_all_hotels_in_city, meta={'state': response.meta['state'], 'city': response.meta['city']})



	def parse_detail_page_link(self, response):

		state = response.meta['state']

		city = response.meta['city']

		item = ChainItem()

		item['Title'] = response.meta['title']

		item['Address'] = self.validate(response.xpath('//span[contains(@class, "hp_address_subtitle")]/text()').extract_first())

		item['Price'] = response.meta['price']

		if item not in self.history:

			self.count[state][city] += 1

			self.history.append(item)
			
			yield item



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