from scrapy.spider import BaseSpider
from scrapy.selector import HtmlXPathSelector

from DCWrapper.items import DcwrapperItem

class DcwrapperSpider(BaseSpider):
    name = "dmoz.org"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dc.uba.ar/aca/materias/obligatorias"
    ]

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
