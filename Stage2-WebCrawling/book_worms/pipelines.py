# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from book_worms.items import BookWormsItem


class BookWormsPipeline(object):
    def process_item(self, item, spider):
        processed_item = {}
        for key in item:
            val = item[key]
            if isinstance(val, list):
                processed_item[key] = [x.encode('UTF8').strip() for x in val]
            else:
                processed_item[key] = val.encode('UTF8').strip()

        return processed_item


class FileWritePipeline(object):
    def process_item(self, item, spider):
        item = self.remove_comma(item)

        if spider.name == 'bookdepository':
            file_name = "bookdepository.csv"

        elif spider.name == 'goodreads':
            file_name = "goodreads.csv"

        else:
            raise Exception("Unknown Spider!")

        fields = ['title', 'authors', 'genres', 'year', 'pages', 'publisher', 'language', 'isbn', 'isbn13', 'url']

        line = ''
        for field in fields:
            value = item.get(field)
            if isinstance(value, list):
                line += ":".join(value)
            else:
                line += str(value)

            line += ','

        line += "\n"
        with open(file_name, 'a') as the_file:
            the_file.write(line)
        return item

    def remove_comma(self, item):
        processed_item = {}

        for key in item:
            val = item[key]
            if isinstance(val, list):
                tmp_list = []
                for list_item in val:
                    p_item = list_item.replace(",", ";")
                    tmp_list.append(p_item)
                processed_item[key] = tmp_list
            else:
                val = val.replace(",", ";")
                processed_item[key] = val

        return processed_item
