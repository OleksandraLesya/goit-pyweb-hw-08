import pika
import json
import logging # Імпортуємо модуль логування
import sys # Імпортуємо модуль sys для sys.exit()
from faker import Faker
from models import Contact # Імпортуємо модель Contact
import connect # noqa: Цей імпорт нашого connect.py ініціалізує підключення до MongoDB Atlas
import random
import configparser # Імпортуємо модуль для роботи з конфігураційними файлами
from typing import Dict, Any, Union # Імпортуємо типи для анотацій

# Ініціалізація Faker для генерації фейкових даних
fake = Faker()

# Налаштування логування для цього модуля
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Читаємо конфігурацію з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Отримуємо параметри RabbitMQ з config.ini
rabbit_host: str = config.get('RABBITMQ', 'host')
email_queue_name: str = config.get('RABBITMQ', 'email_queue')
sms_queue_name: str = config.get('RABBITMQ', 'sms_queue')

# Підключення до RabbitMQ
# Використовуємо BlockingConnection для синхронної роботи
try:
    connection: pika.BlockingConnection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()
    logging.info(f"✅ Успішно підключено до RabbitMQ на хості: {rabbit_host}")
except pika.exceptions.AMQPConnectionError as e:
    logging.error(f"❌ Помилка підключення до RabbitMQ: {e}")
    logging.error("Будь ласка, переконайтеся, що RabbitMQ сервер запущений (наприклад, через Docker).")
    sys.exit(1) # Виходимо, якщо не можемо підключитися

# Оголошення черг
# Якщо черги не існують, RabbitMQ їх створить.
# durable=True означає, що черга переживе перезапуск RabbitMQ
channel.queue_declare(queue=email_queue_name, durable=True)
channel.queue_declare(queue=sms_queue_name, durable=True)
logging.info(f"Оголошено черги: '{email_queue_name}' та '{sms_queue_name}'")

# Генерація фейкових контактів та відправка повідомлень у черги
num_contacts_to_generate: int = 10 # Кількість контактів для генерації

logging.info(f"\nГенеруємо {num_contacts_to_generate} фейкових контактів...")
for i in range(num_contacts_to_generate):
    # Випадковим чином обираємо кращий канал зв'язку для контакту
    preferred_channel: str = random.choice(["email", "sms"])

    # Створюємо новий контакт з фейковими даними
    # is_sent за замовчуванням False, phone_number та preferred_channel заповнюються
    contact: Contact = Contact(
        full_name=fake.name(),
        email=fake.email(),
        phone_number=fake.phone_number(), # Використовуємо phone_number як у моделі
        preferred_channel=preferred_channel
    )
    # Зберігаємо контакт у MongoDB
    try:
        contact.save()
        logging.info(f"   Збережено контакт у MongoDB: {contact.full_name} ({contact.email})")
    except Exception as e:
        logging.error(f"   ❌ Помилка збереження контакту {contact.full_name} у MongoDB: {e}")
        continue # Продовжуємо до наступного контакту, якщо виникла помилка збереження

    # Формуємо дані для повідомлення (тільки ObjectID контакту)
    contact_data: Dict[str, str] = {'contact_id': str(contact.id)} # Перетворюємо ObjectId на рядок

    # Визначаємо, в яку чергу відправляти повідомлення
    queue_to_send: str
    if preferred_channel == "email":
        queue_to_send = email_queue_name
    else: # preferred_channel == "sms"
        queue_to_send = sms_queue_name

    # Відправляємо повідомлення в RabbitMQ
    channel.basic_publish(
        exchange='', # Використовуємо дефолтний exchange (пряма відправка в чергу)
        routing_key=queue_to_send, # Назва черги, в яку відправляємо
        body=json.dumps(contact_data).encode('utf-8'), # Перетворюємо словник на JSON-рядок і кодуємо в байти
        properties=pika.BasicProperties(
            delivery_mode=2, # Зробити повідомлення стійким (persistent)
        )
    )

    logging.info(f"[x] Відправлено '{preferred_channel.upper()}' завдання для контакту: {contact.full_name} (ID: {contact.id}) до черги '{queue_to_send}'")

# Закриття з'єднання з RabbitMQ
connection.close()
logging.info("\nЗавершено генерацію та відправку контактів. З'єднання з RabbitMQ закрито.")
