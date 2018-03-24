# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from book_worms.items import BookWormsItem

import pdb

class BookDepositorySpider(scrapy.Spider):
    name = 'bookdepository'
    allowed_domains = ['bookdepository.com']

    start_urls = []

    templates = [
        'https://www.bookdepository.com/category/358/Romance?page=%s',
        'https://www.bookdepository.com/category/2632/Historical-Romance?page=%s',
        'https://www.bookdepository.com/category/2631/Adult-Contemporary-Romance?page=%s',
        'https://www.bookdepository.com/category/2630/Romance/browse/viewmode/all?page=%s',
        'https://www.bookdepository.com/category/356/Erotic-Fiction?page=%s'
    ]

    for template in templates:
        for i in range(1, 41):
            start_urls.append(template % (i,))

    blacklists = (
        "/*\/gp/*",
        "/*reviews/*",
        "/*gift/*",
        "/*Gift/*",
        "/*stream/*",
        "\/e\/",
        "\/services\/",
        "/*zgbs/*",
        "/*\/b\?/*",
        "chart",
        "/*/s\/",
        "/*credit/*"
        )

    # rules = [
    #     Rule(LinkExtractor(allow=('.*'), deny=blacklists), follow=True, callback="parse_items")
    # ]

    def parse(self, response):
        links = response.selector.xpath("//div[@class='item-info']/h3/a/@href").extract()
        for link in links:
            yield scrapy.Request("https://www.bookdepository.com" + link, callback=self.parse_items)


    def parse_items(self, response):
        item = BookWormsItem()
        item['url'] = response.url
        item['title'] = response.selector.xpath("//div[@class='item-info']/h1/text()").extract()[0]
        item['authors'] = response.selector.xpath("//div[contains(@class,'author-info')]/a/text()").extract()

        item['genres'] = response.selector.xpath("//ol[@class='breadcrumb']/li/a/text()").extract()
        pages = response.selector.xpath("//span[@itemprop='numberOfPages']/text()").extract()
        if len(pages) > 0:
            item['pages'] = pages[0].split()[0]

        publisher = response.selector.xpath("//a[@itemprop='publisher']/text()").extract()
        if len(publisher) > 0:
            item['publisher'] = publisher[0]

        pub_date = response.selector.xpath("//span[@itemprop='datePublished']/text()").extract()
        if len(pub_date) > 0:
            item['year'] = pub_date[0]

        lang = response.selector.xpath("//li[label/text()='Language']/span//text()").extract()
        if len(lang) > 0:
            item['language'] = lang[0]

        isbn10 = response.selector.xpath("//li[label/text()='ISBN10']/span//text()").extract()
        if len(isbn10) > 0:
            item['isbn'] = isbn10[0]

        isbn13 = response.selector.xpath("//li[label/text()='ISBN10']/span//text()").extract()
        if len(isbn13) > 0:
            item['isbn13'] = isbn10[0]

        return item
