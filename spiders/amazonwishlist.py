import scrapy
import re
from urllib.parse import urlparse


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
            #link = item.css('#itemName_'+id + "::attr(href)").extract_first()
            #img = item.css('#itemImage_'+id).css('img::attr(src)').extract_first()
            price = item.css('::attr(data-price)').extract_first()
            obj = {
                'id': id,
                'title': title,
                'price': price
            }

            self.scraped_data.append(obj)
            yield obj

        # manage "infinite scrolldown"
        teste = response.css('input.showMoreUrl::attr(value)').extract_first()
        #has_next = response.css('#sort-by-price-next-batch-lek::attr(value)').extract_first()
        if teste:
            next_page = urlparse(self.BASE_URL + teste).geturl()
            yield scrapy.Request(next_page)

