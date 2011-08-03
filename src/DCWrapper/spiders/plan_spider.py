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

	def sacar_largos(x): return (4<len(x)<40)
	texto = filter(sacar_largos, texto)
	def sacar_espaciosos(x): 
		if(re.search('  ', x)): return 0
		else: return 1 
	texto = filter(sacar_espaciosos, texto)
        def sacar_simbolo(txt): 
                p = re.compile('[(*)]')
                txt = p.sub('', txt)
                return txt.lstrip()
        texto = map(sacar_simbolo, texto)
        def sacar_minusculas(x): 
                if(len(x)>1): return (x[0] == x[0].capitalize())
                else: 0
        texto = filter(sacar_minusculas, texto)
        def sacar_ver(txt): 
                p = re.compile(' ver ')
                txt = p.sub('', txt)
                return txt
        texto = filter(sacar_ver, texto)

	print texto
