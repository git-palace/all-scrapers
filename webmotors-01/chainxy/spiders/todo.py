# from __future__ import unicode_literals
import scrapy

import json

import os

import scrapy

from scrapy.spiders import Spider

from scrapy.http import FormRequest

from scrapy.http import Request

from chainxy.items import ChainItem

from selenium import webdriver

from lxml import etree

from lxml import html

import pdb

import time


class todo(scrapy.Spider):

    name = 'webmotors'

    domain = 'www.webmotors.com.br'

    history = []

    def __init__(self):

        self.driver = webdriver.Chrome("./chromedriver.exe")

        pass

    def start_requests(self):

        url = 'https://www.webmotors.com.br/carros/estoque/alfa-romeo?tipoveiculo=carros&marca1=alfa%20romeo&estadocidade=estoque&qt=36&p=1'

        yield scrapy.Request(url=url, callback=self.repeat_request, meta={'page_id': 1})

    def repeat_request(self, response):

        page_id = response.meta['page_id']

        selector_list = response.xpath('//div[contains(@class, "boxResultado")]/a')

        if len(selector_list) > 0:

            for selector in selector_list:

                item = ChainItem()

                detail_link = selector.xpath('./@href').extract_first()

                item['version_of_year'] = self.validate(selector.xpath('.//span[@class="version"]/text()').extract_first())

                item['financing'] = self.validate('\n'.join(selector.xpath('.//div[@class="mrg-left attributes"]/span/text()').extract()))

                item['city'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

                item['a_type'] = self.validate(selector.xpath('.//div[contains(@class, "card-footer")]/span[1]/text()').extract_first())

                yield scrapy.Request(url=detail_link, callback=self.parse, meta={'item': item})

            page_id += 1

            page_url = 'https://www.webmotors.com.br/carros/estoque/alfa-romeo?tipoveiculo=carros&marca1=alfa%20romeo&estadocidade=estoque&qt=36&p=' + str(page_id)

            yield scrapy.Request(url=page_url, callback=self.repeat_request, meta={'page_id': page_id})

    def parse(self, response):

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

        self.driver.get(response.url)

        self.driver.find_element_by_class_name('versomentetelefone').click()

        time.sleep(2)

        source = self.driver.page_source.encode("utf8")

        tree = etree.HTML(source)

        item['phone_numbers'] = self.validate(', '.join(tree.xpath('//div[@class="txt-telefone"]/b/text()')))

        prv_imgURL_list = response.xpath('//div[contains(@class, "carousel-inner")]//img/@src').extract()

        for imgURL in prv_imgURL_list:

            yield scrapy.Request(imgURL, callback=self.image_download, meta={'pref': 'prv_'})

            imgURL = imgURL.split('?')[0]

            yield scrapy.Request(imgURL, callback=self.image_download, meta={'pref': 'org_'})

        yield item

    def image_download(self, response):

        name = 'images/' + response.meta['pref'] + response.url.split('/')[-1].split('?')[0]

        with open(name, 'wb') as f:

            f.write(response.body)

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
