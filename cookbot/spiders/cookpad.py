#!/usr/bin/env python

import os
import re
import urlparse

from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors.sgml import SgmlLinkExtractor
from scrapy.selector import HtmlXPathSelector

from cookbot.items import CookpadRecipe


class CookpadSpider(CrawlSpider):
    name = 'cookpad'
    allowed_domains = ['cookpad.com']
    download_delay = 1

    start_urls = [
        'http://cookpad.com/category/11', # Meat
        'http://cookpad.com/category/10', # Vegetable
        'http://cookpad.com/category/12', # Fish
        'http://cookpad.com/category/2',  # Rice
        'http://cookpad.com/category/6',  # Pasta / Gratin
        'http://cookpad.com/category/9',  # Noodles
        'http://cookpad.com/category/15', # Stew, soup
    ]

    rules = (
        # Follow pagination
        Rule(SgmlLinkExtractor(allow=(r'category/\d+\?page=\d+',)), follow=True),

        # Extract recipes
        Rule(SgmlLinkExtractor(allow=(r'recipe/\d+',)), callback='parse_recipe')
    )

    def parse_recipe(self, response):
        hxs = HtmlXPathSelector(response)
        recipe = CookpadRecipe()
        recipe['id'] = int(re.findall(r'recipe/(\d+)', response.url)[0])
        recipe['name'] = hxs.select("//div[@id='recipe-title']/h1/text()")[0] \
                            .extract().strip()
        recipe['author'] = int(
            hxs.select("//a[@id='recipe_author_name']/@href").re('(\d+)')[0]
        )
        recipe['description'] = hxs.select("//div[@id='description']/text()")[0] \
                                   .extract().strip()
        recipe['ingredients'] = hxs.select("//div[@class='ingredient_name']/text()") \
                                   .extract()

        referer = response.request.headers.get('Referer')
        recipe['category'] = int(os.path.basename(urlparse.urlsplit(referer).path))

        try:
            recipe['report_count'] = int(
                hxs.select("//li[@id='tsukurepo_tab']/a/span/text()").re('(\d+)')[0]
            )
        except:
            recipe['report_count'] = 0

        try:
            recipe['comment_count'] = int(
                hxs.select("//li[@id='comment_tab']/a/span/text()").re('(\d+)')[0]
            )
        except:
            recipe['comment_count'] = 0
        return recipe
