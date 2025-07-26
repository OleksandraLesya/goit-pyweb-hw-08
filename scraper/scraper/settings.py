# Scrapy settings for scraper project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings in the documentation:
#
# https://docs.scrapy.org/en/latest/topics/settings.html
# https://docs.scrapy.org/en/latest/topics/downloader-middleware.html
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

# Назва бота Scrapy
BOT_NAME = "scraper"

# Модулі зі спайдерами
SPIDER_MODULES = ["scraper.scraper.spiders"]
NEWSPIDER_MODULE = "scraper.scraper.spiders"

# Ідентифікація під час звернення до сайтів
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/126.0.0.0 Safari/537.36"
)

# Поважати правила robots.txt
ROBOTSTXT_OBEY = True

# Обмеження одночасних запитів до одного домену
CONCURRENT_REQUESTS_PER_DOMAIN = 1

# Затримка між запитами (в секундах)
DOWNLOAD_DELAY = 1

# Використання pipeline для обробки елементів
ITEM_PIPELINES = {
   "scraper.scraper.pipelines.ScraperPipeline": 300, # Повний шлях до Pipeline
}

# Налаштування експорту зібраних даних у JSON файли
# Використовуємо FEEDS для експорту QuoteItem в quotes.json
# AuthorItem будуть збережені Pipeline
FEEDS = {
    "data/quotes.json": {
        "format": "json",
        "overwrite": True,  # Перезаписувати файл, якщо він існує
        "encoding": "utf8",
        "item_classes": [
            "scraper.scraper.spiders.quotes.QuoteItem"
        ],  # Вказуємо, які Item'и сюди зберігати
    }
    # ЗАПИС ПРО data/authors.json ВИДАЛЕНО ЗВІДСИ,
    # Оскільки ЙОГО ЗБЕРІГАЄ НАШ PIPELINE!
}

# Усі інші опції залишені за замовчуванням або вимкнені:
# COOKIES_ENABLED = False
# TELNETCONSOLE_ENABLED = False
# AUTOTHROTTLE_ENABLED = True
# HTTPCACHE_ENABLED = True
# SPIDER_MIDDLEWARES = {}
# DOWNLOADER_MIDDLEWARES = {}
# EXTENSIONS = {}
