import pika
import json
from faker import Faker
from models import Contact # Імпортуємо модель Contact
import connect # noqa: Це імпортує наш connect.py, який ініціалізує підключення до MongoDB Atlas
import random
import configparser # Імпортуємо модуль для роботи з конфігураційними файлами

# Ініціалізація Faker для генерації фейкових даних
fake = Faker()

# Читання конфігурації з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Отримання параметрів RabbitMQ з config.ini
rabbit_host = config.get('RABBITMQ', 'host')
email_queue_name = config.get('RABBITMQ', 'email_queue')
sms_queue_name = config.get('RABBITMQ', 'sms_queue')

# Підключення до RabbitMQ
# Використовуємо BlockingConnection для синхронної роботи
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()
    print(f"✅ Успішно підключено до RabbitMQ на хості: {rabbit_host}")
except pika.exceptions.AMQPConnectionError as e:
    print(f"❌ Помилка підключення до RabbitMQ: {e}")
    print("Будь ласка, переконайтеся, що RabbitMQ сервер запущений (наприклад, через Docker).")
    exit(1) # Виходимо, якщо не можемо підключитися

# Оголошення черг
# Якщо черги не існують, RabbitMQ їх створить.
# durable=True означає, що черга переживе перезапуск RabbitMQ
channel.queue_declare(queue=email_queue_name, durable=True)
channel.queue_declare(queue=sms_queue_name, durable=True)
print(f"Оголошено черги: '{email_queue_name}' та '{sms_queue_name}'")

# Генерація фейкових контактів та відправка повідомлень у черги
num_contacts_to_generate = 10 # Кількість контактів для генерації

print(f"\nГенеруємо {num_contacts_to_generate} фейкових контактів...")
for i in range(num_contacts_to_generate):
    # Випадковим чином обираємо кращий канал зв'язку для контакту
    preferred_channel = random.choice(["email", "sms"])

    # Створюємо новий контакт з фейковими даними
    # is_sent за замовчуванням False, phone_number та preferred_channel заповнюються
    contact = Contact(
        full_name=fake.name(),
        email=fake.email(),
        phone_number=fake.phone_number(), # Використовуємо phone_number як у моделі
        preferred_channel=preferred_channel
    )
    # Зберігаємо контакт у MongoDB
    try:
        contact.save()
        print(f"   Збережено контакт у MongoDB: {contact.full_name} ({contact.email})")
    except Exception as e:
        print(f"   ❌ Помилка збереження контакту {contact.full_name} у MongoDB: {e}")
        continue # Продовжуємо до наступного контакту, якщо виникла помилка збереження

    # Формуємо дані для повідомлення (тільки ObjectID контакту)
    contact_data = {'contact_id': str(contact.id)} # Перетворюємо ObjectId на рядок

    # Визначаємо, в яку чергу відправляти повідомлення
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

    print(f"[x] Відправлено '{preferred_channel.upper()}' завдання для контакту: {contact.full_name} (ID: {contact.id}) до черги '{queue_to_send}'")

# Закриття з'єднання з RabbitMQ
connection.close()
print("\nЗавершено генерацію та відправку контактів. З'єднання з RabbitMQ закрито.")

