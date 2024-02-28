from scrapy import Spider, Request

from scrapy.crawler import CrawlerProcess


class QuotesSpider(Spider):
    name = "quotes"
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "./json/quotes.json"}
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]

    def parse(self, response):
        for quote in response.xpath("/html//div[@class='quote']"):
            yield {
                "tags": quote.xpath("div[@class='tags']/a/text()").extract(),
                "author": quote.xpath("span/small/text()").get(),
                "quote": quote.xpath("span[@class='text']/text()").get(),
            }
            next_link = response.xpath("//li[@class='next']/a/@href").get()
            if next_link:
                yield Request(url=self.start_urls[0] + next_link)


class AuthorsSpider(Spider):
    name = "authors"
    custom_settings = {"FEED_FORMAT": "json", "FEED_URI": "./json/authors.json"}
    allowed_domains = ["quotes.toscrape.com"]
    start_urls = ["https://quotes.toscrape.com"]
    authors_set = set()
    authors_list = []

    def parse(self, response):
        if self.authors_list:
            yield {
                "fullname": response.xpath(
                    "/html//h3[@class='author-title']/text()"
                ).get(),
                "born_date": response.xpath(
                    "/html//span[@class='author-born-date']/text()"
                ).get(),
                "born_location": response.xpath(
                    "/html//span[@class='author-born-location']/text()"
                ).get(),
                "description": response.xpath(
                    "/html//div[@class='author-description']/text()"
                )
                .get()
                .strip(),
            }
            for link in self.authors_list:
                yield Request(url=self.start_urls[0] + link)
        else:
            new_links = response.xpath(
                "//a[starts-with(@href, '/author')]/@href"
            ).extract()
            for new_link in new_links:
                self.authors_set.add(new_link)

            next_link = response.xpath("//li[@class='next']/a/@href").get()
            if next_link:
                yield Request(url=self.start_urls[0] + next_link)
            else:
                first_link = ""
                for author_link in self.authors_set:
                    if first_link:
                        self.authors_list.append(author_link)
                    else:
                        first_link = author_link
                yield Request(url=self.start_urls[0] + first_link)


if __name__ == "__main__":
    process = CrawlerProcess()
    process.crawl(QuotesSpider)
    process.crawl(AuthorsSpider)
    process.start()
