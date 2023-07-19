import scrapy
import re
from urllib.parse import urlparse
from model.Wishlist import Wishlist

# https://www.programiz.com/python-programming/examples/check-string-number


class AmazonWishlistSpider(scrapy.Spider):
    BASE_URL = 'https://www.amazon.com.br'
    name = 'amazonwishlist'
    allowed_domains = ['www.amazon.com.br']

    def __init__(self, userToSend, scraped_data, **kwargs):
        self.scraped_data = scraped_data
        uri = userToSend['wishlist']
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
            tem_preco_destacado = item.css('div.price-section span.a-price span.a-offscreen::text').extract_first()
            oferta_desconto = item.css('div.wl-deal-rich-badge-label span::text').extract_first()
            link = item.css('#itemName_'+id + "::attr(href)").extract_first()
            eh_marketplace = item.css('span.wl-item-delivery-badge span::text').extract_first()
            obj = Wishlist(id, title, price, oferta_desconto, link, eh_marketplace, tem_preco_destacado) 
            self.scraped_data.append(obj)
            yield vars(obj)

        # manage "infinite scrolldown"
        has_next = response.css('input.showMoreUrl::attr(value)').extract_first()
        if has_next:
            next_page = urlparse(self.BASE_URL + has_next).geturl()
            yield scrapy.Request(next_page)

