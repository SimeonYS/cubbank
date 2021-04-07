import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import CcubbankItem
from itemloaders.processors import TakeFirst
import json

pattern = r'(\xa0)?'
base = 'https://www.cubbank.com/api/posts?blog%5B%5D=1&count=6&order-by=publish_start_date&locale=en&page={}'

class CcubbankSpider(scrapy.Spider):
	name = 'cubbank'
	page = 1
	start_urls = [base.format(page)]

	def parse(self, response):
		data = json.loads(response.text)
		for index in range(len(data['data'])):
			link = data['data'][index]['full_slug']
			date = data['data'][index]['publish_start_date'].split()[0]
			title = data['data'][index]['title']
			yield response.follow(link, self.parse_post, cb_kwargs=dict(date=date, title=title))

		if data['next_page_url']:
			self.page += 1
			yield response.follow(base.format(self.page), self.parse)

	def parse_post(self, response, date, title):
		content = response.xpath('//div[@class="post-body"]//text()').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))

		item = ItemLoader(item=CcubbankItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
