import json
import os
import sys
from models import Author, Quote # Імпортуємо моделі
from connect import connect_db # Імпортуємо функцію для підключення до БД

# 1. Підключаємося до бази даних MongoDB Atlas
# Це дуже важливо, щоб скрипт міг взаємодіяти з БД
connect_db()

# Шляхи до JSON файлів. Тепер вони вказують на папку 'data'.
# Створюємо повний шлях до файлів, використовуючи os.path.join
DATA_FOLDER = "data"
AUTHORS_FILE_PATH = os.path.join(DATA_FOLDER, "authors.json")
QUOTES_FILE_PATH = os.path.join(DATA_FOLDER, "quotes.json")


# Перевірка наявності JSON файлів
if not os.path.exists(AUTHORS_FILE_PATH):
    print(f"Помилка: Файл {AUTHORS_FILE_PATH} не знайдено.")
    sys.exit(1)

if not os.path.exists(QUOTES_FILE_PATH):
    print(f"Помилка: Файл {QUOTES_FILE_PATH} не знайдено.")
    sys.exit(1)

print(f"Завантажуємо дані з {AUTHORS_FILE_PATH} та {QUOTES_FILE_PATH}...")

try:
    # 2. Відкриваємо та читаємо authors.json
    with open(AUTHORS_FILE_PATH, "r", encoding="utf-8") as f:
        authors_data = json.load(f)

    # 3. Для кожного автора з JSON: Створюємо об'єкт Author та зберігаємо його в БД
    print("Зберігаємо авторів...")
    for author_info in authors_data:
        # Перевіряємо, чи автор вже існує, щоб уникнути дублікатів
        if not Author.objects(fullname=author_info["fullname"]).first():
            Author(**author_info).save()
            # print(f"Збережено автора: {author_info['fullname']}")
        # else:
            # print(f"Автор вже існує (пропущено): {author_info['fullname']}")
    print("Автори збережені.")

    # 4. Відкриваємо та читаємо quotes.json
    with open(QUOTES_FILE_PATH, "r", encoding="utf-8") as f:
        quotes_data = json.load(f)

    # 5. Для кожної цитати з JSON:
    print("Зберігаємо цитати...")
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
                # print(f"Збережено цитату: '{quote_info['quote']}' від {quote_info['author']}")
            # else:
                # print(f"Цитата вже існує (пропущено): '{quote_info['quote']}'")
        else:
            print(f"Помилка: Автор '{quote_info['author']}' для цитати '{quote_info['quote']}' не знайдений в БД. Цитата не буде збережена.")
    print("Цитати збережені.")

    print("Процес завантаження даних завершено успішно! 🎉")

except json.JSONDecodeError as e:
    print(f"Помилка читання JSON файлу: {e}. Перевірте формат JSON.")
    sys.exit(1)
except Exception as e:
    print(f"Виникла невідома помилка під час завантаження даних: {e}")
    sys.exit(1)

