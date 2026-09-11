import sys
import scrapy
from scrapy.crawler import CrawlerProcess

class DotabuffSpider(scrapy.Spider):
    name = "dotabuff_spider"
    start_urls = ['https://dotabuff.com']

    def parse(self, response):
        # Находим строки таблицы с героями.
        # Обычно на Dotabuff используется стандартная структура таблиц внутри tbody.
        # Мы берем tr, которые содержат данные о герое (исключая заголовок)
        rows = response.css('table tbody tr') or response.css('article table tr')
        
        count = 0
        for row in rows:
            if count >= 5:
                break
                
            # Имя героя обычно находится в теге со специальным атрибутом 'data-value' или внутри ссылки/ячейки с именем
            # Используем селектор для ячейки с именем героя (обычно имеет класс .cell-large или содержит ссылку на героя)
            hero_name = row.css('td.cell-large a::text').get() or row.css('td:nth-child(2) a::text').get()
            
            # Винрейт находится в блоке, структуру которого вы присылали ранее
            winrate_text = row.css('div.tw-flex.tw-w-full.tw-flex-col.tw-items-start.tw-gap-1 span::text').get()
            
            # Если по какой-то причине селекторы пустые, пропускаем строку таблицы (например, это заголовок)
            if not hero_name or not winrate_text:
                continue
                
            yield {
                'hero': hero_name.strip(),
                'winrate': winrate_text.strip()
            }
            count += 1

if __name__ == '__main__':
    output_file = sys.argv[1] if len(sys.argv) > 1 else 'output.json'
    
    settings = {
        'FEEDS': {
            output_file: {
                'format': 'json',
                'encoding': 'utf8',
                'overwrite': True,
            },
        },
        'LOG_LEVEL': 'ERROR',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
    }
    
    process = CrawlerProcess(settings)
    process.crawl(DotabuffSpider)
    process.start()