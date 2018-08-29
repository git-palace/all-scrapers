# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

    make_model = Field()

    version_of_year = Field()

    financing = Field()

    city = Field()

    a_type = Field()

    price = Field()

    store_name = Field()

    phone_numbers = Field()

    year = Field()

    mileage = Field()

    exchange = Field()

    fuel = Field()

    color = Field()

    bodywork = Field()

    end_plate = Field()

    items = Field()

    seller_notes = Field()

    images = Field()

    prev_images = Field()