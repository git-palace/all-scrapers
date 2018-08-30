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
		
		url = 'https://www.webmotors.com.br/carro/marcasativas?tipoAnuncio=novos-usados'

		yield scrapy.Request(url=url, callback=self.parse_models)


	# get model list
	def parse_models(self, response):

		models = json.loads(response.body_as_unicode().replace("'", '"'))
		models = models['Common'] + models['Principal']

		for model in models:
			model_title = str(model['N']).lower()

			page_url = ('https://www.webmotors.com.br/carros/estoque/%s?qt=36' % (model_title))

			yield scrapy.Request(url=page_url, callback=self.parse_search_result_page, meta={'page_id': 1, 'page_url': page_url})

			return


	# parse search result page
	def parse_search_result_page(self, response):

		selector_list = response.xpath('//div[contains(@class, "boxResultado")]/a')

		if len(selector_list) > 0:

			for selector in selector_list:
				item = ChainItem()

				detail_link = selector.xpath('./@href').extract_first()

				item['version_of_year'] = self.validate(selector.xpath('.//span[@class="version"]/text()').extract_first())

				item['financing'] = self.validate('\n'.join(selector.xpath('.//div[@class="mrg-left attributes"]/span/text()').extract()))

				item['city'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

				item['a_type'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

				yield scrapy.Request(url=detail_link, callback=self.parse_detail_page, meta={'item': item})

			page_id = response.meta['page_id']
			page_id += 1

			page_url = (('%s&p=%s') % (response.meta['page_url'], page_id))

			yield scrapy.Request(url=page_url, callback=self.parse_search_result_page, meta={'page_id': page_id})


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

		item['items'] = self.validate(', '.join(response.xpath('//div[contains(@class, "size-default")]/div/table//td/text()').extract()))

		item['seller_notes'] = self.validate(response.xpath('//div[contains(@class, "size-default")]//p[@class="info-seller"]/text()').extract_first())

		imgURL_list = response.xpath('//div[contains(@class, "carousel-inner")]//img/@src').extract()

		for imgURL in imgURL_list:

			imgURL = imgURL.split('?')[0]

			yield scrapy.Request(imgURL, callback=self.image_download)

		print item


	# download images
	def image_download(self, response):
		
		name = 'images/' + response.url.split('/')[-1]

		with open(name, 'wb') as f:

			f.write(response.body)