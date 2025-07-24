import configparser
import logging # Імпортуємо модуль logging
from mongoengine import connect as mongo_connect

# Налаштування базового логування
# Це дозволить виводити повідомлення в консоль з різними рівнями важливості
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Читаємо конфігурацію з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

def connect_db() -> None: # Додано анотацію типу для функції (повертає None)
    """
    Функція для підключення до бази даних MongoDB Atlas.
    Використовує параметри з config.ini.
    """
    try:
        # Отримуємо URI підключення з секції MONGO_DB
        mongo_uri: str = config.get('MONGO_DB', 'uri') # Додано анотацію типу для змінної

        # Підключаємося до MongoDB Atlas
        mongo_connect(host=mongo_uri)

        logging.info("✅ Успішно підключено до MongoDB Atlas.") # Використовуємо logging.info
    except configparser.NoSectionError:
        logging.error("❌ Помилка: Секція 'MONGO_DB' не знайдена в config.ini. Будь ласка, перевірте файл конфігурації.") # Використовуємо logging.error
        exit(1)
    except configparser.NoOptionError as e:
        logging.error(f"❌ Помилка: Опція '{e.option}' не знайдена в секції 'MONGO_DB' config.ini.") # Використовуємо logging.error
        exit(1)
    except Exception as e:
        logging.error(f"❌ Помилка підключення до MongoDB Atlas: {e}") # Використовуємо logging.error
        logging.error("Будь ласка, перевірте URI підключення та доступ до мережі.") # Використовуємо logging.error
        exit(1)

# Викликаємо функцію підключення при імпорті модуля
connect_db()
