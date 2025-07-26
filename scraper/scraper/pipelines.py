# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import json
import os
import logging
from typing import Any

from scrapy import Spider
from scrapy.item import Item
from itemadapter import ItemAdapter

# Імпортуємо наші Item'и, які ми визначили у spiders/quotes.py
from scraper.scraper.spiders.quotes import AuthorItem, QuoteItem

# Налаштування логування для Pipeline
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


class ScraperPipeline:
    """
    Scrapy Pipeline для обробки зібраних даних.
    Зберігає унікальних авторів у 'data/authors.json' та пропускає цитати
    для автоматичного збереження через налаштування FEEDS.
    """

    def __init__(self):
        """
        Ініціалізує Pipeline.
        Створює порожній список для авторів та set для відстеження вже збережених авторів
        (за їхнім повним ім'ям), щоб уникнути дублікатів.
        """
        self.authors_data = []  # Список для зберігання даних унікальних авторів
        self.seen_authors = set()  # Set для відстеження унікальних авторів за fullname
        self.authors_file_path = os.path.join('data', 'authors.json')  # Шлях до файлу authors.json

        # Перевіряємо, чи існує папка 'data', якщо ні — створюємо її
        os.makedirs('data', exist_ok=True)
        logging.info(f"Pipeline ініціалізовано. Файл авторів: {self.authors_file_path}")

    def process_item(self, item: Item, spider: Spider) -> Item:
        """
        Обробляє кожен зібраний Item.
        Якщо Item є AuthorItem і автор ще не був збережений, додає його до списку.
        QuoteItem'и просто пропускаються, оскільки вони будуть збережені через FEEDS.
        """
        adapter = ItemAdapter(item)

        if isinstance(item, AuthorItem):
            fullname = adapter.get('fullname')
            if not fullname:
                logging.warning("AuthorItem не має 'fullname', пропускаємо.")
                return item

            if fullname not in self.seen_authors:
                # Зберігаємо тільки потрібні поля автора
                author_dict = {
                    "fullname": adapter.get("fullname"),
                    "born_date": adapter.get("born_date"),
                    "born_location": adapter.get("born_location"),
                    "description": adapter.get("description"),
                }
                self.authors_data.append(author_dict)
                self.seen_authors.add(fullname)
                logging.info(f"Додано унікального автора: {fullname}")
            else:
                logging.debug(f"Автор '{fullname}' вже був оброблений, пропускаємо.")
            return item

        elif isinstance(item, QuoteItem):
            # QuoteItem'и будуть збережені автоматично через FEEDS у settings.py
            logging.debug("Отримано QuoteItem для збереження через FEEDS.")
            return item

        return item  # Повертаємо item для інших Pipeline, якщо вони є

    def close_spider(self, spider: Spider) -> None:
        """
        Викликається, коли павук завершує роботу.
        Зберігає зібрані дані унікальних авторів у файл 'authors.json'.
        """
        logging.info(f"Павук '{spider.name}' завершив роботу. Зберігаємо дані авторів у {self.authors_file_path}")
        try:
            with open(self.authors_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.authors_data, f, ensure_ascii=False, indent=2)
            logging.info(f"Дані авторів успішно збережено у {self.authors_file_path}")
        except Exception as e:
            logging.error(f"Помилка при збереженні авторів: {e}")
