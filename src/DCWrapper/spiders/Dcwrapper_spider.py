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
        sites = hxs.select('//div[@id="parent-fieldname-text"]/ul/li')
        
        #dejo items para saber como lo hace la libreria         
        items = []
        materias = []

        #abrimos la consulta para agregar cada nombre
        c = self.connection.cursor()

        for site in sites:
            item = DcwrapperItem()
            item['title'] = site.select('a/text()').extract()
            #item['link'] = site.select('a/@href').extract()
            #item['desc'] = site.select('text()').extract()
            for i in item['title']:
                print 'HOLA: '+str(i.encode("utf-8"))
                materias.append(str(i.encode("utf-8")))

                s = 'INSERT INTO materias (nombre) VALUES(\''+str(i.encode("utf-8"))+'\')'
                print s
                c.execute(s)
            items.append(item)
    
        c.close()
        
        self.connection.commit()
        self.connection.close()
        print materias        
        print 'Fin: '

        return items

