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
	otros = hxs.select('//div[@id="content"]/div/dl/dt/span[@class="contenttype-news-item summary"]/a/text()').extract()

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
	    #print 'texto:'
            texto.append([titulo, lugar, empieza, termina])

            index = index + 1            
            #for i in titulos:            
            #    print 'Title: '+str(i.encode('utf-8'))
#            for i in materias:
#                print 'Materias: '+str(i.encode('utf-8'))
#            for i in materias1:
#                print 'Materias: '+str(i.encode('utf-8'))

	#print 'descripcion: '+str(descripcion)
	#print 'otros: '+str(otros)

	#recorremos y juntamos la info
	for txt in texto[0:14]:
		if(len(descripcion)>0): 
			descr = descripcion.pop(0)
			txt.append([descr])
	texto[14].append([])
	texto[15].append([descripcion.pop(0)])
	texto[16].append([])
	for txt in texto[17:20]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])
	texto[20].append([])
	for txt in texto[21:27]:
	        if(len(descripcion)>0):
        		descr = descripcion.pop(0)
                	txt.append([descr])
	texto[27].append([])
        for txt in texto[28:30]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])
        texto[30].append([])
        for txt in texto[31:60]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])
	descripcion.pop(0)
        for txt in texto[60:78]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])
        texto[78].append([])        
        for txt in texto[79:86]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])
        texto[86].append([])        
	texto[87].append([])
        for txt in texto[88:]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt.append([descr])

        #texto dividido

        #sacamos espacios al pedo
        for txt in texto:
                for frase in txt:
                        if (len(frase)>0):                
                                p = re.compile('\'')
                                frase[0] = p.sub('', frase[0])    
                                frase[0] = (frase[0].lstrip()).rstrip()
		
        for i in texto:
		print i
		print '\n'

        #guardemos la informacion
        #create table agenda (id INTEGER PRIMARY KEY, titulo TEXT, lugar TEXT, empieza TEXT, termina TEXT, descripcion TEXT);
        self.connection = sqlite3.connect('./database/base1.db')
        self.connection.text_factory = str

        c = self.connection.cursor()

        for txt in texto:
                titulo = str( ((txt[0])[0]).encode('utf-8') )
                lugar = str( ((txt[1])[0]).encode('utf-8') )
                empieza = str( ((txt[2])[0]).encode('utf-8') )
                termina = str( ((txt[3])[0]).encode('utf-8') )
                
                if(len(txt[4]) > 0): descripcion = str( ((txt[4])[0]).encode('utf-8') )
                else: descripcion = ''   

                params = (titulo, lugar, empieza, termina, descripcion, )
                rows = c.execute('SELECT * FROM agenda WHERE titulo=? AND lugar=? AND empieza=? AND termina=? AND descripcion=? ', params)
                if(len(rows.fetchall()) == 0):
                        s = 'INSERT INTO agenda (titulo, lugar, empieza, termina, descripcion) VALUES(\''+str(titulo)+'\', \''+str(lugar)+'\', \''+str(empieza)+'\', \''+str(termina)+'\', \''+str(descripcion)+'\')'
                        print s                        
                        c.execute(s)

        c.close()
        
        self.connection.commit()
        self.connection.close()


