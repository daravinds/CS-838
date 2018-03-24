# -*- coding: utf-8 -*-
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from book_worms.items import BookWormsItem

class GoodReadSpider(CrawlSpider):
  name = 'goodreads'
  allowed_domains = ['goodreads.com']

  start_urls = []
  for i in range(12, 48):
    link = 'https://www.goodreads.com/list/show/12362.All_Time_Favorite_Romance_Novels?page=' + str(i)
    start_urls.append(link)

  black = ("\*list\*", )
  rules = [
    Rule(LinkExtractor(allow=('.*'), restrict_css=(".tableList td a.bookTitle[itemprop='url']"), deny = black), follow=True, callback="parse_items")
  ]

  def parse_items(self, response):
    book_title = response.selector.xpath('//div[contains(@id, "metacol")]')

    if book_title:
      item = BookWormsItem()

      title = response.selector.xpath('//h1[@id = "bookTitle"]/text()').extract()
      if title:
        item['title'] = title[0].strip()

      authors = response.selector.xpath('//div[@id = "bookAuthors"]/span[@itemprop = "author"]/a/span/text()').extract()
      new_authors = list()
      for val in authors:
        new_authors.append(val.strip())
      item['authors'] = new_authors
      pages = response.selector.xpath('//div[@id = "details"]/div/span[@itemprop = "numberOfPages"]/text()').extract()
      if pages:
        item['pages'] = pages[0].split()[0]
      isbn = response.selector.xpath(
          '//div[@id = "bookDataBox"]/div[contains(@class, "clearFloats")]/'
          'div[contains(@class, "infoBoxRowItem")]/text()').extract()
      if isbn:
        item['isbn'] = isbn[1].strip()
      isbn13 = response.selector.xpath(
          '//div[@id = "bookDataBox"]/div[contains(@class, "clearFloats")]/'
          'div[contains(@class, "infoBoxRowItem")]/span/span/text()').extract()
      if isbn13:
        item['isbn13'] = isbn13[0].strip()
      language = response.selector.xpath('//div[@id = "bookDataBox"]/div[contains(@class, "clearFloats")]'
                                                 '/div[contains(@class, "infoBoxRowItem")]/text()').extract()
      if language and len(language) > 3:
        item['language'] = language[3].strip()

      publication = response.selector.xpath('//div[@id = "details"]/div[contains(@class, "row")]/'
                                              'text()').extract()

      splitted = []
      for i in publication:
        if 'Published' in i:
          splitted = i.split('\n')

      s = ''
      string_split = []
      for i in splitted:
        if 'by' in i:
          string_split = i.strip().split(' ')

      for i in string_split:
        if not 'by' in i:
          s = s + i + ' '

      item['publisher'] = s.strip()

      months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October',
                'November', 'December']
      found = False
      pub_year = ''

      for i in splitted:
        for month in months:
          if month in i:
            pub_year = i
            found = True
            break

        if found:
          break

      item['year'] = pub_year.strip()
      item['genres'] = response.selector.xpath('//div[contains(@class, "bigBoxContent containerWithHeaderContent")]'
                                               '/div[contains(@class, "elementList")]/div[contains(@class, "left")]'
                                               '/a/text()').extract()
      genres = item['genres']
      new_genres = list()
      for val in genres:
        new_genres.append(val.strip())
      item['genres'] = new_genres
      item['url'] = response.url
      return item