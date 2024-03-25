from typing import Any
import scrapy
from scrapy.http import Response 

class AosFatos(scrapy.Spider):
  name='aosfatos'
  custom_settings ={
    "HTTPCACHE_ENABLED" :True,
  }
  
  start_urls = ["https://www.aosfatos.org"]
  
  def parse(self, response: Response, **kwargs: Any) -> Any:
    links = response.xpath("//nav//ul//li//a[contains(@href, 'checamos')]/@href").getall()[:-1]
    for link in links:
      yield scrapy.Request(
          response.urljoin(link),
          callback=self.parse_category
      )
  def parse_category(self, response):
    news = response.css('a.entry-item-card::attr(href)').getall()
    for news_url in news:
      yield scrapy.Request(
        response.urljoin(news_url),
        callback=self.parse_news
      )
    pages_url = response.css('span.step-links a::attr(href)').getall()[:10]
    urls = [item.replace('#', '') for item in pages_url if item != '#' and int(item.split('=')[1]) <= 3]
    for page in urls:
      yield scrapy.Request(
        response.urljoin(page),
        callback=self.parse_category
      )
  def parse_news(self, response):
    title = response.css('article>h1::text').get(),
    date =' '.join(response.css('div.publish-date::text').get().split()) ,
    quotes =response.css("article blockquote")
    for quote in quotes:
      qoute_text = quote.css('::text').get()
      # status = quote.xpath('substring-after(//blockquote/preceding-sibling::p/img/@src, "/static/images/stamps/")').get()
      status = response.xpath('//blockquote/preceding-sibling::p/img/@alt').get()
      if status is None:
        status = quote.xpath('substring-after(//blockquote/preceding-sibling::p/img/@src, "/static/images/stamps/")').get()
        status = status.replace(".png", "")
      if status is '':
        status = response.xpath('//blockquote/preceding-sibling::p/a/img/@alt').get()
      yield{
        'title': title,
        'date' : date,
        'text': qoute_text,
        'status': status,
        'url': response.url
      }
