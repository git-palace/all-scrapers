import scrapy
import json
import os
from scrapy.spiders import Spider
from scrapy.http import FormRequest
from scrapy.http import Request
from chainxy.items import ChainItem
from lxml import etree
from lxml import html
import pdb


class todo(scrapy.Spider):
	name = 'webmotors'
	domain = 'www.webmotors.com.br'
	history = []

	def __init__(self):
		pass


	# validate
	def validate(self, item):
		try:
			return item.replace('\n', '').replace('\t', '').replace('\r', '').strip()
		except:
			pass


	# start scrapy
	def start_requests(self):
		
		for model_type in ['carro', 'moto']:

			url = ('https://www.webmotors.com.br/%s/marcasativas' % (model_type))

			yield scrapy.Request(url=url, callback=self.parse_models, meta={'m_type': model_type})


	# get model list
	def parse_models(self, response):

		models = json.loads(response.body_as_unicode().replace("'", '"'))
		models = models['Common'] + models['Principal']
		m_type = response.meta['m_type']

		for model in models:
			model_title = model['N'].encode('utf-8').strip().lower().replace(' ', '-')

			search_page_url = ('https://www.webmotors.com.br/%ss/estoque/%s?qt=36' % (m_type, model_title))

			yield scrapy.Request(url=search_page_url, callback=self.parse_search_result_page, meta={'page_id': 1, 'search_page_url': search_page_url, 'm_type': m_type})


	# parse search result page
	def parse_search_result_page(self, response):
		
		m_type = response.meta['m_type']

		selector_list = response.xpath('//div[contains(@class, "boxResultado")]/a')

		if len(selector_list) > 0:

			for selector in selector_list:
				item = ChainItem()

				detail_link = selector.xpath('./@href').extract_first()

				item['version_of_year'] = self.validate(selector.xpath('.//span[@class="version"]/text()').extract_first())

				item['financing'] = self.validate('\n'.join(selector.xpath('.//div[@class="mrg-left attributes"]/span/text()').extract()))

				item['city'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

				item['a_type'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

				yield scrapy.Request(url=detail_link, callback=self.parse_detail_page, meta={'item': item, 'm_type': m_type})

			page_id = response.meta['page_id']
			page_id += 1

			search_page_url = (('%s&p=%s') % (response.meta['search_page_url'], page_id))

			yield scrapy.Request(url=search_page_url, callback=self.parse_search_result_page, meta={'page_id': page_id, 'm_type': m_type, 'search_page_url': response.meta['search_page_url']})


	# parse detail page
	def parse_detail_page(self, response):

		item = response.meta['item']

		item['make_model'] = self.validate(response.xpath('//span[contains(@class, "makemodel")]/text()').extract_first())

		item['price'] = self.validate(response.xpath('//span[contains(@class, "b__price")]/text()').extract_first())

		item['store_name'] = self.validate(response.xpath('//strong[@class="store-name"]/text()').extract_first())

		item['year'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[1]/td[1]/span/text()').extract_first())

		item['mileage'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[1]/td[2]/span/text()').extract_first())

		item['exchange'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[1]/td[3]/span/text()').extract_first())

		item['fuel'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[1]/td[4]/span/text()').extract_first())

		item['color'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[2]/td[1]/span/text()').extract_first())

		item['bodywork'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[2]/td[2]/span/text()').extract_first())

		item['end_plate'] = self.validate(response.xpath('//div[@class="vehicle-details__main-info"]/table//tr[2]/td[3]/span/text()').extract_first())

		item['items'] = self.validate('\n'.join(response.xpath('//div[contains(@class, "size-default")]/div/table//td/text()').extract()))

		item['seller_notes'] = self.validate(response.xpath('//div[contains(@class, "size-default")]//p[@class="info-seller"]/text()').extract_first())

		imgURL_list = response.xpath('//div[contains(@class, "carousel-inner")]//img/@src').extract()

		images = []

		for imgURL in imgURL_list:

			imgURL = imgURL.split('?')[0]

			images.append(imgURL)

			yield scrapy.Request(imgURL, callback=self.image_download)

		item['images'] = '\n'.join(images)

		code = self.validate(response.xpath('//form/input[@name="codigoAnuncio"]/@value').extract_first())

		m_type = response.meta['m_type']

		phone_url = ('https://www.webmotors.com.br/comprar/versomentetelefone?codigoAnuncio=%s&tipoVeiculo=%s' % (code, m_type))

		yield scrapy.Request(url=phone_url, callback=self.parse_phone_number, meta={'item': item})


	# download images
	def image_download(self, response):
		
		name = 'images/' + response.url.split('/')[-1]

		with open(name, 'wb') as f:

			f.write(response.body)


	# parse phone number
	def parse_phone_number(self, response):
		phone_list = json.loads(response.body_as_unicode().replace("'", '"'))

		phone_numbers = []

		for phone in phone_list:
			phone_numbers.append(phone['Telefone'])

		item = response.meta['item']

		item['phone_numbers'] = '\n'.join(phone_numbers)

		yield item
