from scrapy.crawler import CrawlerProcess
from spiders.amazonwishlist import AmazonWishlistSpider


def get_data(usersToSend):
    process = CrawlerProcess(settings={
        'FEED_FORMAT': 'json',
        'LOG_LEVEL': 'ERROR'
    })
   
    scraped_data_by_user = []
    for userToSend in usersToSend:
        scraped_data = []
        process.crawl(AmazonWishlistSpider, userToSend, scraped_data)
        scraped_data_by_user.append({
            'userId': userToSend['userId'],
            'items': scraped_data
        })
        
    process.start(stop_after_crawl=True)
    return scraped_data_by_user

