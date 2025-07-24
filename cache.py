import redis
import json
import sys

# Ініціалізація Redis клієнта
# host: адреса Redis сервера (для локального Redis це 'localhost')
# port: порт Redis сервера (стандартний порт 6379)
# db: номер бази даних Redis (за замовчуванням 0)
# decode_responses=True: автоматично декодує відповіді Redis у рядки Python (UTF-8)
try:
    r = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # Спробуємо зробити просту операцію, щоб перевірити з'єднання
    r.ping()
    print("✅ Успішно підключено до Redis!")
except redis.exceptions.ConnectionError as e:
    print(f"❌ Помилка підключення до Redis: {e}")
    print("Будь ласка, переконайтеся, що Redis сервер запущений на 'localhost:6379'.")
    sys.exit(1) # Виходимо, якщо не можемо підключитися до Redis
except Exception as e:
    print(f"Невідома помилка при ініціалізації Redis: {e}")
    sys.exit(1)

def get_cache(key):
    """
    Отримує дані з кешу Redis за ключем.
    Повертає розпарсений JSON-об'єкт або None, якщо ключ не знайдено.
    """
    cached_data = r.get(key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            print(f"Помилка декодування JSON для ключа '{key}' з Redis.")
            return None
    return None

def set_cache(key, value, ttl=300):
    """
    Зберігає дані у кеш Redis за ключем.
    Дані конвертуються у JSON-рядок.
    ttl (time to live): час життя кешу в секундах (за замовчуванням 300 секунд = 5 хвилин).
    """
    try:
        # json.dumps перетворює Python-об'єкт на JSON-рядок
        # ensure_ascii=False дозволяє зберігати не-ASCII символи (наприклад, кирилицю) без екранування
        r.set(key, json.dumps(value, ensure_ascii=False), ex=ttl)
    except Exception as e:
        print(f"Помилка запису даних у Redis для ключа '{key}': {e}")

