import redis
import json
import sys
import logging # Імпортуємо модуль logging
from typing import Any, Optional # Імпортуємо типи для анотацій

# Налаштування логування для цього модуля
# Це дозволить виводити повідомлення в консоль з різними рівнями важливості
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Ініціалізація Redis клієнта
# host: адреса Redis сервера (для локального Redis це 'localhost')
# port: порт Redis сервера (стандартний порт 6379)
# db: номер бази даних Redis (за замовчуванням 0)
# decode_responses=True: автоматично декодує відповіді Redis у рядки Python (UTF-8)
try:
    r: redis.Redis = redis.StrictRedis(host='localhost', port=6379, db=0, decode_responses=True)
    # Спробуємо зробити просту операцію, щоб перевірити з'єднання
    r.ping()
    logging.info("✅ Успішно підключено до Redis!") # Використовуємо logging.info
except redis.exceptions.ConnectionError as e:
    logging.error(f"❌ Помилка підключення до Redis: {e}") # Використовуємо logging.error
    logging.error("Будь ласка, переконайтеся, що Redis сервер запущений на 'localhost:6379'.") # Використовуємо logging.error
    sys.exit(1) # Виходимо, якщо не можемо підключитися до Redis
except Exception as e:
    logging.error(f"Невідома помилка при ініціалізації Redis: {e}") # Використовуємо logging.error
    sys.exit(1)

def get_cache(key: str) -> Optional[Any]:
    """
    Отримує дані з кешу Redis за ключем.
    Повертає розпарсений JSON-об'єкт або None, якщо ключ не знайдено.
    """
    cached_data: Optional[str] = r.get(key)
    if cached_data:
        try:
            return json.loads(cached_data)
        except json.JSONDecodeError:
            logging.error(f"Помилка декодування JSON для ключа '{key}' з Redis.") # Використовуємо logging.error
            return None
    return None

def set_cache(key: str, value: Any, ttl: int = 300) -> None:
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
        logging.error(f"Помилка запису даних у Redis для ключа '{key}': {e}") # Використовуємо logging.error
