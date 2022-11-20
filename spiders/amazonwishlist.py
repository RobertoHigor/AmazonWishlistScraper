import scrapy
import re
from urllib.parse import urlparse
import math

# https://www.programiz.com/python-programming/examples/check-string-number
def try_parse_float(num):
    try:
        convertedValue = float(num)
        if math.isinf(convertedValue):
            return 0
        return convertedValue
    except ValueError:
        return 0

class AmazonWishlistSpider(scrapy.Spider):
    BASE_URL = 'https://www.amazon.com.br'
    name = 'amazonwishlist'
    allowed_domains = ['www.amazon.com.br']

    def __init__(self, uri, scraped_data, **kwargs):
        self.scraped_data = scraped_data
        self.start_urls = [uri]

        domain = re.sub(r'(http|https)?://', '', uri)
        self.allowed_domains.append(domain)

        super().__init__(**kwargs)   

    def parse(self, response):
        page_items = response.css(".g-item-sortable")

        for item in page_items:
            id = item.css('li::attr(data-itemid)').extract_first()
            title = item.css('#itemName_'+id + "::attr(title)").extract_first()
            price = item.css('::attr(data-price)').extract_first()
            ofertaDesconto = item.css('div.wl-deal-rich-badge-label span::text').extract_first()
            link = item.css('#itemName_'+id + "::attr(href)").extract_first()
            obj = {
                'id': id,
                'title': title,
                'price': try_parse_float(price),
                'oferta': ofertaDesconto,
                'link': self.BASE_URL + link
            }       

            self.scraped_data.append(obj)
            yield obj

        # manage "infinite scrolldown"
        has_next = response.css('input.showMoreUrl::attr(value)').extract_first()
        if has_next:
            next_page = urlparse(self.BASE_URL + has_next).geturl()
            yield scrapy.Request(next_page)

