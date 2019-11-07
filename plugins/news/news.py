import scrapy
from scrapy.crawler import CrawlerProcess



# hotnews.ro spider

class HotNews(scrapy.Spider):
    name = 'hotnews'
    start_urls = ['https://hotnews.ro']

    def parse(self, response):
        for title in response.css('h2.article_title'):
            news_item = title.css('a ::text').get()
            print(news_item)


def testtest():
    print("TEEEEEEEEEEEEEEST!")
process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(HotNews)
process.start()
process.stop()