import random

import scrapy
import random
from bookscraper.items import BookItem


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com/"]

    custom_settings = {
        'FEEDS': {
            # Overwriting settings
            'cleandata.csv': {'format': 'csv', 'overwrite': True}
        }
    }

    def parse(self, response):
        # creating iterable of all 'books' in <article class=product_pod
        books = response.css('article.product_pod')
        for book in books:
            # Getting relative url from <h3 <a href=
            relative_url = book.css('h3 a ::attr(href)').get()
            if 'catalogue/' in relative_url:
                book_url = 'https://books.toscrape.com/' + relative_url
            else:
                # Adding catalogue/ if not present
                book_url = 'https://books.toscrape.com/catalogue/' + relative_url
            # sending each 'book' to parse_book_page function, with book_url and random user-agent from the list
            yield response.follow(book_url, callback=self.parse_book_page)

        # Getting url for next page, <li class=next <a href=
        next_page = response.css('li.next a ::attr(href)').get()

        if next_page is not None:
            if 'catalogue/' in next_page:
                next_page_url = 'https://books.toscrape.com/' + next_page
            else:
                next_page_url = 'https://books.toscrape.com/catalogue/' + next_page
            # Calling parse (this function) function with url of next page and random user-agent from the list
            yield response.follow(next_page_url, callback=self.parse)

    def parse_book_page(self, response):

        # Getting table <table <tr
        table_rows = response.css('table tr')
        book_item = BookItem()

        book_item['url'] = response.url,
        book_item['title'] = response.css('.product_main h1::text').get(),
        # Getting each row from a table
        book_item['upc'] = table_rows[0].css("td ::text").get(),
        book_item['product_type' ] = table_rows[1].css("td ::text").get(),
        book_item['price_excl_tax'] = table_rows[2].css("td ::text").get(),
        book_item['price_incl_tax'] = table_rows[3].css("td ::text").get(),
        book_item['tax'] = table_rows[4].css("td ::text").get(),
        book_item['availability'] = table_rows[5].css("td ::text").get(),
        book_item['num_reviews'] = table_rows[6].css("td ::text").get(),
        book_item['stars'] = response.css("p.star-rating").attrib['class'],
        # xpath, complicated stuff, got to learn this
        book_item['category'] = response.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
        book_item['description'] = response.xpath("//div[@id='product_description']/following-sibling::p/text()").get()

        yield book_item

