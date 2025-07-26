import logging
import sys
import json
from concurrent.futures import ThreadPoolExecutor
import re


from run_scraper import run_scrapy_spider

from connect import connect_db
from cache import r as redis_client, get_cache, set_cache
from models import Author, Quote
from mongoengine import Q

# Налаштування логування для main.py
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# Функція для пошуку цитат за ім'ям автора
def search_quotes_by_author(author_name):
    """
    Шукає цитати за повним або частковим ім'ям автора.
    Використовує Redis для кешування результатів.
    """
    cache_key = f"author:{author_name.lower()}"
    cached_result = get_cache(cache_key)

    if cached_result:
        logging.info(">>> From Redis:")
        quotes_data = cached_result
        for quote_data in quotes_data:
            logging.info(
                f"- \"{quote_data['quote']}\" - {quote_data['author']} (Теги: {', '.join(quote_data['tags'])})")
        return

    logging.info(">>> From MongoDB:")

    # ВИПРАВЛЕНО: Спочатку знаходимо авторів за іменем
    # Використовуємо iregex для пошуку за частковим ім'ям без урахування регістру
    authors = Author.objects(fullname__iregex=f"^{re.escape(author_name)}").all()

    if not authors:
        logging.info("Автора з таким ім'ям не знайдено.")
        return

    # Збираємо ID знайдених авторів
    author_ids = [author.id for author in authors]

    # Тепер шукаємо цитати, які посилаються на цих авторів за їхніми ID
    quotes = Quote.objects(author__in=author_ids).all()

    if quotes:
        quotes_data = []
        for quote in quotes:
            quotes_data.append({
                "quote": quote.quote,
                "author": quote.author.fullname,
                "tags": [tag for tag in quote.tags]
            })
        set_cache(cache_key, quotes_data, ttl=3600)
        for quote_data in quotes_data:
            logging.info(
                f"- \"{quote_data['quote']}\" - {quote_data['author']} (Теги: {', '.join(quote_data['tags'])})")
    else:
        logging.info("Цитат за цим автором не знайдено.")


# Функція для пошуку цитат за тегом
def search_quotes_by_tag(tag_name):
    """
    Шукає цитати за повним або частковим тегом.
    Використовує Redis для кешування результатів.
    """
    cache_key = f"tag:{tag_name.lower()}"
    cached_result = get_cache(cache_key)

    if cached_result:
        logging.info(">>> From Redis:")
        quotes_data = cached_result
        for quote_data in quotes_data:
            logging.info(
                f"- \"{quote_data['quote']}\" - {quote_data['author']} (Теги: {', '.join(quote_data['tags'])})")
        return

    logging.info(">>> From MongoDB:")
    quotes = Quote.objects(tags__iregex=f"^{re.escape(tag_name)}").all()
    if quotes:
        quotes_data = []
        for quote in quotes:
            quotes_data.append({
                "quote": quote.quote,
                "author": quote.author.fullname,
                "tags": [tag for tag in quote.tags]
            })
        set_cache(cache_key, quotes_data, ttl=3600)
        for quote_data in quotes_data:
            logging.info(
                f"- \"{quote_data['quote']}\" - {quote_data['author']} (Теги: {', '.join(quote_data['tags'])})")
    else:
        logging.info("Цитат за цим тегом не знайдено.")


# Функція для пошуку цитат за кількома тегами
def search_quotes_by_tags(tag_names):
    """
    Шукає цитати за кількома тегами (логічне АБО).
    Не кешується в Redis.
    """
    logging.info(">>> From MongoDB (множинні теги не кешуються):")
    tags_query = [Q(tags__in=[tag.strip()]) for tag in tag_names]
    combined_query = Q()
    for q_obj in tags_query:
        combined_query |= q_obj

    quotes = Quote.objects(combined_query).all()

    if quotes:
        for quote in quotes:
            logging.info(
                f"- \"{quote.quote}\" - {quote.author.fullname} (Теги: {', '.join(tag for tag in quote.tags)})")
    else:
        logging.info("Цитат за вказаними тегами не знайдено.")


# Головна функція CLI-додатку
def run_cli_app():
    """
    Запускає інтерактивний CLI-додаток для пошуку цитат.
    """
    logging.info(
        "\nПідключено до бази даних. Введіть команду для пошуку (наприклад, 'name: Albert Einstein', 'tag: life', 'tags: humor,funny') або 'exit' для виходу.")
    logging.info("Результати з кешу Redis будуть позначені '>>> From Redis:', з MongoDB - '>>> From MongoDB:'.")
    logging.info("Тепер також підтримується скорочений пошук, наприклад, 'name: al' або 'tag: li'.")

    while True:
        command = input(">>> ").strip()
        if command.lower() == 'exit':
            logging.info("Вихід з програми.")
            break
        elif command.lower().startswith('name:'):
            author_name = command[len('name:'):].strip()
            search_quotes_by_author(author_name)
        elif command.lower().startswith('tag:'):
            tag_name = command[len('tag:'):].strip()
            search_quotes_by_tag(tag_name)
        elif command.lower().startswith('tags:'):
            tag_names_str = command[len('tags:'):].strip()
            tag_names = [t.strip() for t in tag_names_str.split(',')]
            search_quotes_by_tags(tag_names)
        else:
            logging.info(
                "Невідома команда. Будь ласка, використовуйте 'name: <автор>', 'tag: <тег>', 'tags: <тег1,тег2>' або 'exit'.")


# Головна точка входу в програму
if __name__ == '__main__':
    connect_db()

    print("\nОберіть дію:")
    print("1. Запустити Scrapy (збір даних)")
    print("2. Запустити CLI-додаток (пошук цитат)")
    print("3. Вийти")

    choice = input("Ваш вибір (1, 2 або 3): ").strip()

    if choice == '1':
        run_scrapy_spider()
    elif choice == '2':
        run_cli_app()
    elif choice == '3':
        logging.info("Вихід з програми.")
        sys.exit(0)
    else:
        logging.info("Некоректний вибір. Будь ласка, перезапустіть програму та оберіть 1, 2 або 3.")
