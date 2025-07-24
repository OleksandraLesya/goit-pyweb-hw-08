import sys
import json # Додаємо імпорт json для pretty-print
from models import Author, Quote # Імпортуємо моделі
from connect import connect_db # Імпортуємо функцію для підключення до БД
from cache import get_cache, set_cache # Імпортуємо функції кешування

def search_quotes_cli():
    """
    Функція для запуску CLI-додатку пошуку цитат з підтримкою кешування Redis.
    Дозволяє шукати цитати за ім'ям автора, одним тегом або кількома тегами.
    Додано можливість скороченого запису значень для пошуку за допомогою регулярних виразів.
    """
    # 1. Підключаємося до бази даних MongoDB Atlas
    # Функція connect_db() вже виводить повідомлення про успішне підключення або помилку.
    connect_db()

    print("\nПідключено до бази даних. Введіть команду для пошуку (наприклад, 'name: Albert Einstein', 'tag: life', 'tags: humor,funny') або 'exit' для виходу.")
    print("Результати з кешу Redis будуть позначені '>>> From Redis:', з MongoDB - '>>> From MongoDB:'.")
    print("Тепер також підтримується скорочений пошук, наприклад, 'name: al' або 'tag: li'.")

    while True:
        user_input = input(">>> ").strip() # Отримуємо введення користувача
        if user_input.lower() == 'exit':
            print("Вихід з програми.")
            break # Виходимо з циклу, якщо користувач ввів 'exit'

        if ":" not in user_input:
            print("Некоректний формат. Використовуйте 'name: [ім'я]', 'tag: [тег]', 'tags: [тег1],[тег2]' або 'exit'.")
            continue

        key, value = user_input.split(":", 1)
        key = key.strip().lower() # Перетворюємо ключ на нижній регістр для зручності
        value = value.strip()

        if not value:
            print(f"Будь ласка, вкажіть значення для '{key}'.")
            continue

        # Формуємо ключ для кешу Redis
        cache_key = f"{key}:{value}"

        # 1. Спробуємо отримати дані з кешу Redis
        cached_result = get_cache(cache_key)
        if cached_result:
            print("\n>>> From Redis:")
            # Виводимо кешовані результати
            for item in cached_result:
                print(f"- \"{item['quote']}\" - {item['author']} (Теги: {', '.join(item['tags'])})")
            continue # Переходимо до наступної ітерації циклу, якщо дані знайдені в кеші

        # 2. Якщо даних немає в кеші, шукаємо в MongoDB
        print("\n>>> From MongoDB:")
        quotes_from_db = [] # Список для зберігання результатів з БД

        if key == "name":
            # Використовуємо __iregex для пошуку за частиною імені (регістронезалежно)
            authors = Author.objects(fullname__iregex=f"^{value}") # ^ означає "починається з"
            if authors:
                for author in authors:
                    quotes = Quote.objects(author=author)
                    if quotes:
                        for q in quotes:
                            quotes_from_db.append({
                                "quote": q.quote,
                                "author": q.author.fullname,
                                "tags": q.tags
                            })
            if not quotes_from_db: # Якщо після перебору авторів нічого не знайшли
                print(f"Цитат від автора, ім'я якого починається з '{value}', не знайдено.")


        elif key == "tag":
            # Використовуємо __iregex для пошуку за частиною тегу (регістронезалежно)
            quotes = Quote.objects(tags__iregex=f"^{value}") # ^ означає "починається з"
            if quotes:
                for q in quotes:
                    quotes_from_db.append({
                        "quote": q.quote,
                        "author": q.author.fullname,
                        "tags": q.tags
                    })
            else:
                print(f"Цитат з тегом, що починається з '{value}', не знайдено.")

        elif key == "tags":
            tags_list = [t.strip() for t in value.split(',') if t.strip()]
            if not tags_list:
                print("Будь ласка, вкажіть дійсні теги.")
                continue
            # Залишаємо __all для пошуку цитат, що містять ВСІ вказані теги
            quotes = Quote.objects(tags__all=tags_list)
            if quotes:
                for q in quotes:
                    quotes_from_db.append({
                        "quote": q.quote,
                        "author": q.author.fullname,
                        "tags": q.tags
                    })
            else:
                print(f"Цитат з тегами '{', '.join(tags_list)}' не знайдено.")
        else:
            print("Невідома команда.")
            continue # Переходимо до наступної ітерації циклу

        # 3. Якщо знайшли дані в MongoDB, зберігаємо їх у кеш Redis
        if quotes_from_db:
            set_cache(cache_key, quotes_from_db) # Зберігаємо список словників
            # Виводимо результати, отримані з MongoDB
            for item in quotes_from_db:
                print(f"- \"{item['quote']}\" - {item['author']} (Теги: {', '.join(item['tags'])})")
        elif not cached_result: # Якщо не було нічого в кеші і нічого не знайшли в БД
            print("Нічого не знайдено за вашим запитом.")


# Запускаємо CLI-додаток, якщо скрипт запускається безпосередньо
if __name__ == "__main__":
    search_quotes_cli()
