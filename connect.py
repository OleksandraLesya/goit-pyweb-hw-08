import configparser
from mongoengine import connect as mongo_connect # Перейменовуємо, щоб уникнути конфлікту з іменем файлу

# Читаємо конфігурацію з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

def connect_db():
    """
    Функція для підключення до бази даних MongoDB Atlas.
    Використовує параметри з config.ini.
    """
    try:
        # Отримуємо URI підключення з секції MONGO_DB
        mongo_uri = config.get('MONGO_DB', 'uri')

        # Підключаємося до MongoDB Atlas
        mongo_connect(host=mongo_uri)

        print(f"✅ Успішно підключено до MongoDB Atlas.")
    except configparser.NoSectionError:
        print("❌ Помилка: Секція 'MONGO_DB' не знайдена в config.ini. Будь ласка, перевірте файл конфігурації.")
        exit(1)
    except configparser.NoOptionError as e:
        print(f"❌ Помилка: Опція '{e.option}' не знайдена в секції 'MONGO_DB' config.ini.")
        exit(1)
    except Exception as e:
        print(f"❌ Помилка підключення до MongoDB Atlas: {e}")
        print("Будь ласка, перевірте URI підключення та доступ до мережі.")
        exit(1)

# Викликаємо функцію підключення при імпорті модуля
connect_db()

