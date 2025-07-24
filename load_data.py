import json
import os
import sys
import logging # Імпортуємо модуль logging
from typing import List, Dict, Any # Імпортуємо типи для анотацій

from models import Author, Quote # Імпортуємо моделі
from connect import connect_db # Імпортуємо функцію для підключення до БД

# Налаштування логування для цього модуля
# Використовуємо той же базовий формат, що і в connect.py, але можна налаштувати окремо
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# 1. Підключаємося до бази даних MongoDB Atlas
# Це дуже важливо, щоб скрипт міг взаємодіяти з БД
connect_db()

# Шляхи до JSON файлів. Тепер вони вказують на папку 'data'.
# Створюємо повний шлях до файлів, використовуючи os.path.join
DATA_FOLDER: str = "data" # Анотація типу
AUTHORS_FILE_PATH: str = os.path.join(DATA_FOLDER, "authors.json") # Анотація типу
QUOTES_FILE_PATH: str = os.path.join(DATA_FOLDER, "quotes.json") # Анотація типу


# Перевірка наявності JSON файлів
if not os.path.exists(AUTHORS_FILE_PATH):
    logging.error(f"Помилка: Файл {AUTHORS_FILE_PATH} не знайдено.") # Використовуємо logging.error
    sys.exit(1)

if not os.path.exists(QUOTES_FILE_PATH):
    logging.error(f"Помилка: Файл {QUOTES_FILE_PATH} не знайдено.") # Використовуємо logging.error
    sys.exit(1)

logging.info(f"Завантажуємо дані з {AUTHORS_FILE_PATH} та {QUOTES_FILE_PATH}...") # Використовуємо logging.info

try:
    # 2. Відкриваємо та читаємо authors.json
    with open(AUTHORS_FILE_PATH, "r", encoding="utf-8") as f:
        authors_data: List[Dict[str, Any]] = json.load(f) # Анотація типу

    # 3. Для кожного автора з JSON: Створюємо об'єкт Author та зберігаємо його в БД
    logging.info("Зберігаємо авторів...") # Використовуємо logging.info
    for author_info in authors_data:
        # Перевіряємо, чи автор вже існує, щоб уникнути дублікатів
        if not Author.objects(fullname=author_info["fullname"]).first():
            Author(**author_info).save()
            logging.info(f"Збережено автора: {author_info['fullname']}") # Використовуємо logging.info
        else:
            logging.info(f"Автор вже існує (пропущено): {author_info['fullname']}") # Використовуємо logging.info (було закоментовано, але корисно для дебагу)
    logging.info("Автори збережені.") # Використовуємо logging.info

    # 4. Відкриваємо та читаємо quotes.json
    with open(QUOTES_FILE_PATH, "r", encoding="utf-8") as f:
        quotes_data: List[Dict[str, Any]] = json.load(f) # Анотація типу

    # 5. Для кожної цитати з JSON:
    logging.info("Зберігаємо цитати...") # Використовуємо logging.info
    for quote_info in quotes_data:
        # Знаходимо відповідного автора в БД за fullname
        author = Author.objects(fullname=quote_info["author"]).first()
        if author:
            # Створюємо об'єкт Quote, використовуючи знайдений об'єкт автора
            # Перевіряємо, чи цитата вже існує, щоб уникнути дублікатів
            if not Quote.objects(quote=quote_info["quote"], author=author).first():
                Quote(
                    quote=quote_info["quote"],
                    tags=quote_info["tags"],
                    author=author
                ).save()
                logging.info(f"Збережено цитату: '{quote_info['quote']}' від {quote_info['author']}") # Використовуємо logging.info
            else:
                logging.info(f"Цитата вже існує (пропущено): '{quote_info['quote']}'") # Використовуємо logging.info (було закоментовано, але корисно для дебагу)
        else:
            logging.error(f"Помилка: Автор '{quote_info['author']}' для цитати '{quote_info['quote']}' не знайдений в БД. Цитата не буде збережена.") # Використовуємо logging.error
    logging.info("Цитати збережені.") # Використовуємо logging.info

    logging.info("Процес завантаження даних завершено успішно! 🎉") # Використовуємо logging.info

except json.JSONDecodeError as e:
    logging.error(f"Помилка читання JSON файлу: {e}. Перевірте формат JSON.") # Використовуємо logging.error
    sys.exit(1)
except Exception as e:
    logging.error(f"Виникла невідома помилка під час завантаження даних: {e}") # Використовуємо logging.error
    sys.exit(1)
