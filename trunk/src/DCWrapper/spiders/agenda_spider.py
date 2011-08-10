# -*- coding: iso-8859-15 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import *

from DCWrapper.items import DcwrapperItem

import sqlite3, re, string

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

        textos = []
        index = 0        
        for site in sites:
            item = DcwrapperItem()

            titulo = site.select('span[@class="contenttype-event summary"]/a[@class="state-published url"]/text()').extract()
            lugar = site.select('span[@class="documentByLine"]/span/span[@class="location"]/text()').extract()           
            empieza = site.select('span[@class="documentByLine"]/span/abbr[@class="dtstart"]/text()').extract()          
            termina = site.select('span[@class="documentByLine"]/span/abbr[@class="dtend"]/text()').extract()             
            url = site.select('span[@class="contenttype-event summary"]/a[@class="state-published url"]/@href').extract()
            
            #analizamos aca titulo para dividir en nombre y tipo
            titulo = titulo[0]
            lugar = lugar[0]
            empieza = empieza[0]
            termina = termina[0]
            url = url[0]
            tipo = ''
            nombre = ''
            

            eventos = ['Defensa Tesis Licenciatura', 'Defensa Tesis Doctorado', 'Charla', 'Defensa Tesis Maestria', 'Seminario', 'Curso' ]
            
            
            for ev in eventos:
                if(re.search(ev, str(titulo.encode('utf-8')) )):
                    tipo = ev
                    p = re.compile(ev)
                    nombre = p.sub('', titulo)
                    p = re.compile(':')
                    nombre = p.sub('', nombre) 
                    break
                
            dicc = {'titulo': titulo, 'tipo': tipo, 'nombre': nombre, 'lugar': lugar, 'empieza': empieza, 'termina': termina, 'url': url }
            textos.append(dicc)            

            index = index + 1            

	#recorremos y juntamos la info

        print textos        

	for txt in textos[0:14]:
		if(len(descripcion)>0): 
			descr = descripcion.pop(0)
			txt['descripcion'] = descr
	textos[14]['descripcion'] = ''
	textos[15]['descripcion'] = descripcion.pop(0)
	textos[16]['descripcion'] = ''
	for txt in textos[17:20]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
        		txt['descripcion'] = descr
	textos[20]['descripcion'] = ''
	for txt in textos[21:27]:
	        if(len(descripcion)>0):
        		descr = descripcion.pop(0)
                	txt['descripcion'] = descr
	textos[27]['descripcion'] = ''
        for txt in textos[28:30]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                	txt['descripcion'] = descr
	textos[30]['descripcion'] = ''
        for txt in textos[31:60]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt['descripcion'] = descr
	descripcion.pop(0)
        for txt in textos[60:78]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt['descripcion'] = descr
        textos[78]['descripcion'] = ''        
        for txt in textos[79:86]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt['descripcion'] = descr
        textos[86]['descripcion'] = ''
	textos[87]['descripcion'] = ''
        for txt in textos[88:]:
                if(len(descripcion)>0):
                        descr = descripcion.pop(0)
                        txt['descripcion'] = descr

        #texto dividido

        #sacamos espacios al pedo

        def sacar_espacios(frase):
                if (len(frase)>0):                
                        p = re.compile('\'')
                        frase = p.sub('', frase)    
                        frase = (frase.lstrip()).rstrip()
                        return frase
                else: return frase        
        
        for txt in textos:
                txt['titulo'] = sacar_espacios(txt['titulo'])
                txt['tipo'] = sacar_espacios(txt['tipo'])
                txt['nombre'] = sacar_espacios(txt['nombre'])
                txt['lugar'] = sacar_espacios(txt['lugar'])
                txt['termina'] = sacar_espacios(txt['termina'])
                txt['empieza'] = sacar_espacios(txt['empieza'])
                txt['descripcion'] = sacar_espacios(txt['descripcion'])
                txt['url'] = sacar_espacios(txt['url'])
                         
        for i in textos:
		print i
		print '\n'

        #guardemos la informacion
        #create table agenda (id INTEGER PRIMARY KEY, titulo TEXT, nombre TEXT, tipo TEXT, lugar TEXT, empieza TEXT, termina TEXT, descripcion TEXT, url TEXT);
        self.connection = sqlite3.connect('./database/base3.db')
        self.connection.text_factory = str

        c = self.connection.cursor()

        for txt in textos:
                titulo = str( (txt['titulo']).encode('utf-8') )
                tipo = str( (txt['tipo']).encode('utf-8') )
                nombre = str( (txt['nombre']).encode('utf-8') )      
                lugar = str( (txt['lugar']).encode('utf-8') )
                empieza = str( (txt['empieza']).encode('utf-8') )
                termina = str( (txt['termina']).encode('utf-8') )
                descripcion = str( (txt['descripcion']).encode('utf-8') )
                url = str( (txt['url']).encode('utf-8') )
                
                params = (titulo, tipo, nombre, lugar, empieza, termina, descripcion, url, )
                rows = c.execute('SELECT * FROM agenda WHERE titulo=? AND tipo=? AND nombre=? AND lugar=? AND empieza=? AND termina=? AND descripcion=? AND url=?', params)
                if(len(rows.fetchall()) == 0):
                        s = 'INSERT INTO agenda (titulo, tipo, nombre, lugar, empieza, termina, descripcion, url) VALUES(\''+str(titulo)+'\', \''+str(tipo)+'\', \''+str(nombre)+'\', \''+str(lugar)+'\', \''+str(empieza)+'\', \''+str(termina)+'\', \''+str(descripcion)+'\', \''+str(url)+'\')'
                        print s                        
                        c.execute(s)

        c.close()
        
        self.connection.commit()
        self.connection.close()


