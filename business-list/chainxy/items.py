# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

    business_name = Field()

    phone = Field()

    lat = Field()

    lng = Field()

    website = Field()

    detail_link = Field()

    email = Field()