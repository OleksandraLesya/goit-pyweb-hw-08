import pika
import json
from models import Contact # Імпортуємо модель Contact
import connect # noqa: Це імпортує наш connect.py, який ініціалізує підключення до MongoDB Atlas
import configparser # Імпортуємо модуль для роботи з конфігураційними файлами
# from mongoengine import connect as mongo_connect # Цей імпорт більше не потрібен, оскільки ми видалили явний блок підключення

# Читання конфігурації з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Отримання параметрів RabbitMQ з config.ini
rabbit_host = config.get('RABBITMQ', 'host')
email_queue_name = config.get('RABBITMQ', 'email_queue')

def callback(ch, method, properties, body):
    """
    Функція зворотного виклику, яка обробляє отримані повідомлення з черги.
    """
    try:
        # Розпарсимо JSON-рядок з тіла повідомлення в Python-словник
        contact_data = json.loads(body)
        contact_id = contact_data.get("contact_id") # Отримуємо 'contact_id'

        if not contact_id:
            print(f"Помилка: Повідомлення не містить 'contact_id': {body.decode('utf-8')}")
            ch.basic_ack(method.delivery_tag) # Підтверджуємо, щоб видалити некоректне повідомлення
            return

        # Знаходимо контакт у MongoDB за його ObjectID
        # MongoEngine може автоматично конвертувати рядок ObjectID у відповідний тип
        contact = Contact.objects(id=contact_id).first()

        if contact:
            if not contact.is_sent: # Перевіряємо, чи повідомлення ще не було надіслано
                print(f"📩 Імітація надсилання EMAIL до {contact.full_name} на {contact.email}")
                # Функція-заглушка: тут могла б бути реальна логіка відправки email
                # наприклад, затримка часу: time.sleep(1)

                # Оновлюємо поле is_sent на True в базі даних
                contact.update(is_sent=True)
                print(f"   ✅ Статус EMAIL для {contact.full_name} оновлено на 'надіслано'.")
            else:
                print(f"   ℹ️ EMAIL для {contact.full_name} вже був надісланий раніше.")
        else:
            print(f"   ❌ Контакт з ID {contact_id} не знайдено в базі даних.")

        # Підтверджуємо, що повідомлення було успішно оброблено
        # Це видаляє повідомлення з черги RabbitMQ
        ch.basic_ack(method.delivery_tag)

    except json.JSONDecodeError:
        print(f"❌ Помилка декодування JSON: {body.decode('utf-8')}")
        ch.basic_ack(method.delivery_tag) # Підтверджуємо, щоб видалити некоректне повідомлення
    except Exception as e:
        print(f"❌ Невідома помилка при обробці повідомлення: {e}")
        print(f"   Повідомлення: {body.decode('utf-8')}")
        # Якщо виникла помилка, можна відхилити повідомлення (basic_nack)
        # або перемістити його в чергу "мертвих листів" (Dead Letter Queue) для подальшого аналізу.
        # Для простоти, поки що підтверджуємо, щоб не заблокувати чергу.
        ch.basic_ack(method.delivery_tag)


# Підключення до RabbitMQ
try:
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel = connection.channel()
    print(f"✅ Успішно підключено до RabbitMQ на хості: {rabbit_host}")
except pika.exceptions.AMQPConnectionError as e:
    print(f"❌ Помилка підключення до RabbitMQ: {e}")
    print("Будь ласка, переконайтеся, що RabbitMQ сервер запущений (наприклад, через Docker).")
    exit(1)

# Оголошення черги (повинна бути такою ж, як і в producer)
channel.queue_declare(queue=email_queue_name, durable=True)

# Вказуємо RabbitMQ, що цей consumer буде отримувати повідомлення з даної черги
# on_message_callback: функція, яка буде викликана при отриманні повідомлення
# auto_ack=False: ми будемо вручну підтверджувати обробку повідомлення (ch.basic_ack)
# Це краще, ніж auto_ack=True, бо гарантує, що повідомлення не загубиться,
# якщо обробка завершиться помилкою до підтвердження.
channel.basic_consume(queue=email_queue_name, on_message_callback=callback, auto_ack=False)

print(f"\n[*] Очікування EMAIL повідомлень з черги '{email_queue_name}'. Для виходу натисніть CTRL+C")
# Запускаємо нескінченний цикл, який чекає на повідомлення
channel.start_consuming()

