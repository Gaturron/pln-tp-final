# -*- coding: iso-8859-15 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import *

from DCWrapper.items import DcwrapperItem

import sqlite3, re

class AgendaSpider(BaseSpider):
    name = "agenda"
    allowed_domains = ["www.dc.uba.ar"]
    start_urls = [
        "http://www.dc.uba.ar/agenda"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@id="content"]/div/dl/dt[@class="vevent"]')
        
        descripcion = hxs.select('//div[@id="content"]/div/dl/dd/span[@class="description"]/text()').extract()          

        texto = []
        index = 0        
        for site in sites:
            item = DcwrapperItem()
#            titulos = site.extract()
            titulo = site.select('span[@class="contenttype-event summary"]/a[@class="state-published url"]/text()').extract()
            lugar = site.select('span[@class="documentByLine"]/span/span[@class="location"]/text()').extract()           
            empieza = site.select('span[@class="documentByLine"]/span/abbr[@class="dtstart"]/text()').extract()          
            termina = site.select('span[@class="documentByLine"]/span/abbr[@class="dtend"]/text()').extract()             
            
            
            #texto.append(str(titulos.encode('utf-8')))
            print [titulo, lugar, empieza, termina, [descripcion[index]]]

            index = index + 1            
            #for i in titulos:            
            #    print 'Title: '+str(i.encode('utf-8'))
#            for i in materias:
#                print 'Materias: '+str(i.encode('utf-8'))
#            for i in materias1:
#                print 'Materias: '+str(i.encode('utf-8'))

