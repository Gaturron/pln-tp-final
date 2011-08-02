# -*- coding: iso-8859-15 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import *

from DCWrapper.items import DcwrapperItem

import sqlite3, re

class PlanSpider(BaseSpider):
    name = "plan"
    allowed_domains = ["www.dc.uba.ar"]
    start_urls = [
        "http://www.dc.uba.ar/aca/carr/grado/licenciatura/plan"
    ]

    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@id="content"]/div[@id="parent-fieldname-text"]//text()')
        
        texto = []
        for site in sites:
            item = DcwrapperItem()
            titulos = site.extract()
#            materias = site.select('p/text()').extract()
#            materias1 = site.select('p//a/text()').extract()            
            texto.append(str(titulos.encode('utf-8')))
            #for i in titulos:            
            #    print 'Title: '+str(i.encode('utf-8'))
#            for i in materias:
#                print 'Materias: '+str(i.encode('utf-8'))
#            for i in materias1:
#                print 'Materias: '+str(i.encode('utf-8'))

        print texto
