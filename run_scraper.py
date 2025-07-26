import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
import os
import logging

# Налаштування логування для скрипта запуску
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Імпортуємо наш павук
# Шлях до павука: scraper/scraper/spiders/quotes.py
from scraper.scraper.spiders.quotes import QuotesSpider, QuoteItem, AuthorItem

def run_scrapy_spider():
    """
    Запускає Scrapy павука для збору цитат та авторів.
    Дані будуть збережені у 'data/quotes.json' та 'data/authors.json'.
    """
    logging.info("=== Початок процесу скрапінгу ===") # Покращене логування

    # Отримуємо налаштування проекту Scrapy (з scraper/scraper/settings.py)
    os.environ['SCRAPY_SETTINGS_MODULE'] = 'scraper.scraper.settings'
    settings = get_project_settings()

    # Ініціалізуємо CrawlerProcess з налаштуваннями
    process = CrawlerProcess(settings)

    # Додаємо наш павук до процесу
    process.crawl(QuotesSpider)

    # Запускаємо процес скрапінгу
    process.start() # Блокує виконання, доки скрапінг не завершиться
    logging.info("=== Завершення процесу скрапінгу ===") # Покращене логування

if __name__ == '__main__':
    # Перевіримо, чи існує папка 'data', якщо ні - створюємо її
    os.makedirs('data', exist_ok=True) # Покращення: створення папки data

    # Перед запуском скрапінгу, перевіримо, чи існують файли data/quotes.json та data/authors.json
    # і видалимо їх, щоб переконатися, що ми починаємо з чистого аркуша.
    quotes_path = os.path.join('data', 'quotes.json')
    authors_path = os.path.join('data', 'authors.json')

    if os.path.exists(quotes_path):
        os.remove(quotes_path)
        logging.info(f"Видалено існуючий файл: {quotes_path}")
    if os.path.exists(authors_path):
        os.remove(authors_path)
        logging.info(f"Видалено існуючий файл: {authors_path}")

    run_scrapy_spider()
