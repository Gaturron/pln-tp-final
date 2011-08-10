# -*- coding: iso-8859-15 -*-

from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector
from scrapy.http import *

from DCWrapper.items import DcwrapperItem

import sqlite3, re

class DcwrapperSpider(BaseSpider):
    name = "materias"
    allowed_domains = ["www.dc.uba.ar"]
    start_urls = [
        #"http://www.dc.uba.ar/aca/materias/obligatorias"
        "http://www.dc.uba.ar/materias"
    ]

    def __init__(self):

        print 'Inicio: '
        self.connection = sqlite3.connect('./database/base3.db')
        self.connection.text_factory = str
      
    def parse(self, response):
        hxs = HtmlXPathSelector(response)
        #sites = hxs.select('//div[@id="parent-fieldname-text"]/ul/li')
        sites = hxs.select('//div[@id="content"]/div/dl/dt/span')
        
        #dejo items para saber como lo hace la libreria         
        items = []

        #abrimos la consulta para agregar cada nombre
        c = self.connection.cursor()

        for site in sites:
            item = DcwrapperItem()
            item['title'] = site.select('a/text()').extract()
            item['link'] = site.select('a/@href').extract()
            #item['desc'] = site.select('text()').extract()

            for i in item['title']:
                print 'Item title: '+str(i.encode('utf-8'))

            for i in item['link']:
                request = Request(i, callback=self.parseMateria, errback=self.mierda)
                yield request
    
        c.close()
        
        self.connection.commit()
        self.connection.close()
        print 'Fin: '

    def mierda(self, response):
        pass

    def parseMateria(self, response):
        
        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@id="content"]//span[@id="parent-fieldname-title"]/text()')
        for site in sites:
            item = DcwrapperItem()
            item['title'] = site.extract()
            materia = str(item['title'].encode('utf-8'))            

        hxs = HtmlXPathSelector(response)
        sites = hxs.select('//div[@id="content"]/div[@id="parent-fieldname-text"]//text()')
        
        texto = ''        
        for site in sites:
            item = DcwrapperItem()
            item['title'] = site.extract()
            texto = texto +'\n'+ str(item['title'].encode('utf-8'))
        
        #En texto tengo todo el parrafo en string
        #print 'Texto: '+str(texto)        
        texto = re.split('(Profesores|Jefes de Trabajos Prácticos|Ayudantes de Primera|Ayudantes de Segunda|Horarios|Puntaje|Correlativas)', texto)

        puntaje = ''
        horario = ''

        index = 0
        i1 = 0
        i2 = 0
        i3 = 0
        i4 = 0
        for parte in texto:
            if(re.search('grado', parte)): puntaje = parte
            if(re.search('(Lunes|Martes|Miércoles|Jueves|Viernes|hs|Depto|curso)', parte)): horario = horario+parte
            if(re.search('Profesores', parte)): i1 = index
            if(re.search('Jefes de Trabajos Prácticos', parte)): i2 = index
            if(re.search('Ayudantes de Primera', parte)): i3 = index
            if(re.search('Ayudantes de Segunda', parte)): i4 = index
            index = index + 1   

        if(i1 != 0): profesores = str(texto[i1+1])
        else: profesores = ''   
        if(i2 != 0): jtps = str(texto[i2+1])
        else: jtps = ''        
        if(i3 != 0): ay1 = str(texto[i3+1])
        else: ay1 = ''        
        if(i4 != 0): ay2 = str(texto[i4+1])
        else: ay2 = ''        

        def limpiar(txt):
            p = re.compile('( [ ]+ |[:])')
            txt = p.sub(' ', txt)
            txt = re.split('[ ]*\n[ ]*', txt)
            def saca_vacios(x): return (len(x) > 2)
            txt = filter(saca_vacios, txt)
            return txt

        materia = limpiar(materia)
        profesores = limpiar(profesores)
        jtps = limpiar(jtps)
        ay1 = limpiar(ay1)
        ay2 = limpiar(ay2)
        puntaje = limpiar(puntaje)
        horario = limpiar(horario)

        def concatenar(l):
            res = ''            
            for x in l:
                res = res+' '+str(x)
            res = res.lstrip()
            return res

        materia = concatenar(materia)
        horario = concatenar(horario)
        puntaje = concatenar(puntaje)

        print 'materia:' + str(materia)
        print 'Profesores: '+str(profesores)
        print 'Jtps: '+str(jtps)
        print 'ay1: '+str(ay1)
        print 'ay2: '+str(ay2)
        print 'Puntaje: '+str(puntaje)
        print 'Horario: '+str(horario)

        #guardemos la informacion
        self.connection = sqlite3.connect('./database/base3.db')
        self.connection.text_factory = str

        c = self.connection.cursor()

        #guardamos nombre horario y puntaje
        nombre = (str(materia),)
        rows = c.execute('SELECT * FROM materias WHERE nombre=?', nombre)
        if(len(rows.fetchall()) == 0):
            s = 'INSERT INTO materias (nombre, horario, puntaje) VALUES(\''+str(materia)+'\', \''+str(horario)+'\', \''+str(puntaje)+'\')'
            c.execute(s)        

        #guardamos info de gente de la materia
        for profesor in profesores:
            #busco si esta guardado
            nombre = (str(profesor),)
            rows = c.execute('SELECT * FROM profesores WHERE nombre=?', nombre)
            #sino esta lo creo            
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO profesores (nombre) VALUES(\''+str(profesor)+'\')'
                c.execute(s)  

            #saco el id de materia y de prof para crear dicta
            c.execute('SELECT id FROM profesores WHERE nombre=?', (str(profesor),) )
            idp = str(c.fetchone()[0])
            c.execute('SELECT id FROM materias WHERE nombre=?', (str(materia),) )
            idm = str(c.fetchone()[0])
            rol = 'Profesor'
            dicta = (str(idp), str(idm), str(rol),)
            rows = c.execute('SELECT * FROM dicta WHERE idp=? AND idm=? AND rango=?', dicta)
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO dicta (idp, idm, rango) VALUES(\''+str(idp)+'\', \''+str(idm)+'\', \''+str(rol)+'\')'
                c.execute(s)  

        for jtp in jtps:
            #busco si esta guardado
            nombre = (str(jtp),)
            rows = c.execute('SELECT * FROM profesores WHERE nombre=?', nombre)
            #sino esta lo creo            
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO profesores (nombre) VALUES(\''+str(jtp)+'\')'
                c.execute(s)  

            #saco el id de materia y de prof para crear dicta
            c.execute('SELECT id FROM profesores WHERE nombre=?', (str(jtp),) )
            idp = str(c.fetchone()[0])
            c.execute('SELECT id FROM materias WHERE nombre=?', (str(materia),) )
            idm = str(c.fetchone()[0])
            rol = 'Jefe de Trabajos Prácticos'
            dicta = (str(idp), str(idm), str(rol),)
            rows = c.execute('SELECT * FROM dicta WHERE idp=? AND idm=? AND rango=?', dicta)
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO dicta (idp, idm, rango) VALUES(\''+str(idp)+'\', \''+str(idm)+'\', \''+str(rol)+'\')'
                c.execute(s)  

        for ay in ay1:
            #busco si esta guardado
            nombre = (str(ay),)
            rows = c.execute('SELECT * FROM profesores WHERE nombre=?', nombre)
            #sino esta lo creo            
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO profesores (nombre) VALUES(\''+str(ay)+'\')'
                c.execute(s)  

            #saco el id de materia y de prof para crear dicta
            c.execute('SELECT id FROM profesores WHERE nombre=?', (str(ay),) )
            idp = str(c.fetchone()[0])
            c.execute('SELECT id FROM materias WHERE nombre=?', (str(materia),) )
            idm = str(c.fetchone()[0])
            rol = 'Ayudantes de Primera'
            dicta = (str(idp), str(idm), str(rol),)
            rows = c.execute('SELECT * FROM dicta WHERE idp=? AND idm=? AND rango=?', dicta)
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO dicta (idp, idm, rango) VALUES(\''+str(idp)+'\', \''+str(idm)+'\', \''+str(rol)+'\')'
                c.execute(s)  

        for ay in ay2:
            #busco si esta guardado
            nombre = (str(ay),)
            rows = c.execute('SELECT * FROM profesores WHERE nombre=?', nombre)
            #sino esta lo creo            
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO profesores (nombre) VALUES(\''+str(ay)+'\')'
                c.execute(s)  

            #saco el id de materia y de prof para crear dicta
            c.execute('SELECT id FROM profesores WHERE nombre=?', (str(ay),) )
            idp = str(c.fetchone()[0])
            c.execute('SELECT id FROM materias WHERE nombre=?', (str(materia),) )
            idm = str(c.fetchone()[0])
            rol = 'Ayudantes de Segunda'
            dicta = (str(idp), str(idm), str(rol),)
            rows = c.execute('SELECT * FROM dicta WHERE idp=? AND idm=? AND rango=?', dicta)
            if(len(rows.fetchall()) == 0):
                s = 'INSERT INTO dicta (idp, idm, rango) VALUES(\''+str(idp)+'\', \''+str(idm)+'\', \''+str(rol)+'\')'
                c.execute(s)  

        c.close()
        
        self.connection.commit()
        self.connection.close()

