from scrapy.spider import BaseSpider
from scrapy.selector import Selector
from scrapy.http import Request
import MySQLdb


class YoutubeSpider(BaseSpider):
    name = 'youtube_spider'
    start_urls = ['https://rrflora.com/']

    def __init__(self, *args, **kwargs):
        self.conn = MySQLdb.connect(host="localhost", user="root", passwd='01491a0237db', db="rrfloradb", charset='utf8', use_unicode=True)
        self.cur = self.conn.cursor()

    def parse(self, response):
        selector = Selector(response)
        article_nodes = selector.xpath('//div[@id="posts"]/article')
        for node in article_nodes:
            title = ''.join(node.xpath('./div[@class="entry-inner"]//header/h2/a/text()').extract())
            link = ''.join(node.xpath('./div[@class="entry-inner"]//header/h2/a/@href').extract())
            desc = ''.join(node.xpath('.//div[@class="entry-content"]/p/text()').extract())
            image = ''.join(node.xpath('./div[@class="entry-media"]/@style').extract())

            yield Request(link, callback=self.parse_next, meta={'title_main': title, 'desc': desc, 'image': image})

    def parse_next(self, response):
        sel = Selector(response)
        title = response.meta['title_main']
        desc  = response.meta['desc']
        image = response.meta['image']
        image_nodes = sel.xpath('//div[@class="entry-content"]/figure')
        for image_node in image_nodes:
            pic = ''.join(image_node.xpath('./a/@href').extract())
            qry = 'insert into images (title, image_desc, image_1, image_2) values (%s, %s, %s, %s) on duplicate key update title = %s'
            values = (title, desc, image, pic, title)
            self.cur.execute(qry, values)
	    self.conn.commit()
