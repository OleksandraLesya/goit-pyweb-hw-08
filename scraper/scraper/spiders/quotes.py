import scrapy
import logging  # Імпортуємо модуль логування
from scrapy.item import Item, Field  # Для визначення структури даних

# Налаштування логування для павука
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Визначення структури для цитат
class QuoteItem(Item):
    """
    Визначає структуру даних для цитат.
    """
    quote = Field()
    author = Field()
    tags = Field()


# Визначення структури для авторів
class AuthorItem(Item):
    """
    Визначає структуру даних для авторів, що відповідає формату ДЗ8.
    """
    fullname = Field()
    born_date = Field()
    born_location = Field()
    description = Field()


class QuotesSpider(scrapy.Spider):
    """
    Павук Scrapy для збору цитат та інформації про авторів з quotes.toscrape.com.
    Обробляє пагінацію та збирає деталі про авторів з їхніх сторінок 'About'.
    """
    name = 'quotes'  # Ім'я павука
    allowed_domains = ['quotes.toscrape.com']  # Дозволені домени для скрапінгу
    start_urls = ['http://quotes.toscrape.com/']  # Починаємо з першої сторінки

    def __init__(self, *args, **kwargs):
        """
        Ініціалізація павука.
        Використовує set для зберігання унікальних посилань на сторінки авторів,
        щоб уникнути повторного скрапінгу та дублікатів.
        """
        super().__init__(*args, **kwargs)
        self.authors_scraped = set()  # Використовуємо set для зберігання вже скраплених URL авторів
        logging.info("Павук QuotesSpider ініціалізовано.")

    def parse(self, response):
        """
        Парсить головну сторінку з цитатами.
        Збирає цитати, авторів, теги та генерує запити для сторінок авторів та пагінації.
        """
        logging.info(f"Парсинг сторінки: {response.url}")

        # Збираємо дані для кожної цитати на поточній сторінці
        for quote_block in response.css('div.quote'):  # Використовуємо CSS-селектори
            quote_item = QuoteItem()
            # Витягуємо текст цитати, видаляючи зайві пробіли та лапки
            quote_item['quote'] = quote_block.css('span.text::text').get().strip().strip('“”')  # Покращення strip()

            author_name = quote_block.css('small.author::text').get()
            quote_item['author'] = author_name

            # Витягуємо теги (список)
            quote_item['tags'] = quote_block.css('div.tags a.tag::text').getall()
            yield quote_item  # Повертаємо зібрану цитату

            # Знаходимо посилання на сторінку "About" автора
            author_about_link = quote_block.css('a[href*="/author/"]::attr(href)').get()

            # Якщо посилання на автора знайдено І посилання на сторінку автора ще не було скраплено
            if author_about_link and author_about_link not in self.authors_scraped:  # Покращення логіки дедуплікації
                self.authors_scraped.add(author_about_link)  # Додаємо УНІКАЛЬНЕ посилання автора до set
                logging.info(f"Знайдено посилання на сторінку автора '{author_name}': {author_about_link}")
                # Генеруємо новий запит для переходу на сторінку автора
                yield response.follow(author_about_link, callback=self.parse_author_details)

        # Логіка пагінації: знаходимо посилання на наступну сторінку
        next_page_link = response.css('li.next a::attr(href)').get()
        if next_page_link:
            logging.info(f"Знайдено посилання на наступну сторінку: {next_page_link}")
            # Генеруємо новий запит для переходу на наступну сторінку
            yield response.follow(next_page_link,
                                  callback=self.parse)  # Обробляємо наступну сторінку тим же методом parse

    def parse_author_details(self, response):
        """
        Парсить сторінку 'About' автора.
        Збирає повне ім'я, дату народження, місце народження та опис автора.
        """
        logging.info(f"Парсинг сторінки автора: {response.url}")
        author_item = AuthorItem()

        # Повне ім'я автора
        author_item['fullname'] = response.css('h3.author-title::text').get().strip()
        # Дата народження
        author_item['born_date'] = response.css('.author-born-date::text').get().strip()
        # Місце народження
        author_item['born_location'] = response.css('.author-born-location::text').get().strip()
        # Опис автора
        author_item['description'] = response.css('.author-description::text').get().strip()

        yield author_item  # Повертаємо зібрані дані про автора
