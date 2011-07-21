from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from DCWrapper.items import DcwrapperItem

import sqlite3

class DcwrapperSpider(BaseSpider):
    name = "dmoz.org"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dc.uba.ar/aca/materias/obligatorias"
    ]

    def __init__(self):

        print 'Inicio: '
        self.connection = sqlite3.connect('./database/base.db')

        c = self.connection.cursor()
        rows = c.execute('SELECT * FROM materias')
        for row in rows:
            print str(row[0])
            print str(row[1])
        
        c.close()
        
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//ul/li')
        items = []
        for site in sites:
            item = DcwrapperItem()
            item['title'] = site.select('a/text()').extract()
            #item['link'] = site.select('a/@href').extract()
            #item['desc'] = site.select('text()').extract()
            items.append(item)
            print 'HOLA: '+str(item['title'])
        return items

    def __del__(self):
        self.connection.commit()
        self.connection.close()
        print 'Fin: '
