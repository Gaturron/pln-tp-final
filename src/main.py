from DCWrapper.spiders import *
import os

os.system('scrapy crawl materias')
#os.system('scrapy crawl plan')
os.system('scrapy crawl agenda')

