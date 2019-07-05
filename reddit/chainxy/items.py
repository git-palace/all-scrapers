# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class ChainItem(Item):

    username = Field()

    comment_time = Field()

    comment_content = Field()

    comment_link = Field()

    post_title = Field()

    post_link = Field()