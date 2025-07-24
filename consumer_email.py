import pika
import json
import logging # Імпортуємо модуль логування
import sys
from typing import Dict, Any, Optional # Імпортуємо типи для анотацій

from models import Contact # Імпортуємо модель Contact
import connect # noqa: Цей імпорт нашого connect.py ініціалізує підключення до MongoDB Atlas
import configparser # Імпортуємо модуль для роботи з конфігураційними файлами

# Налаштування логування для цього модуля
# Це дозволить виводити повідомлення в консоль з різними рівнями важливості
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Читаємо конфігурацію з config.ini
config = configparser.ConfigParser()
config.read('config.ini')

# Отримуємо параметри RabbitMQ з config.ini
rabbit_host: str = config.get('RABBITMQ', 'host')
email_queue_name: str = config.get('RABBITMQ', 'email_queue')

def callback(ch: pika.adapters.blocking_connection.BlockingChannel, method: pika.spec.Basic.Deliver, properties: pika.spec.BasicProperties, body: bytes) -> None:
    """
    Функція зворотного виклику, яка обробляє отримані повідомлення з черги.
    """
    try:
        # Розпарсимо JSON-рядок з тіла повідомлення в Python-словник
        contact_data: Dict[str, Any] = json.loads(body)
        contact_id: Optional[str] = contact_data.get("contact_id") # Отримуємо 'contact_id'

        if not contact_id:
            logging.warning(f"Попередження: Повідомлення не містить 'contact_id': {body.decode('utf-8')}")
            ch.basic_ack(method.delivery_tag) # Підтверджуємо, щоб видалити некоректне повідомлення
            return

        # Знаходимо контакт у MongoDB за його ObjectID
        # MongoEngine може автоматично конвертувати рядок ObjectID у відповідний тип
        contact: Optional[Contact] = Contact.objects(id=contact_id).first()

        if contact:
            if not contact.is_sent: # Перевіряємо, чи повідомлення ще не було надіслано
                logging.info(f"📩 Імітація надсилання EMAIL до {contact.full_name} на {contact.email}")
                # Функція-заглушка: тут могла б бути реальна логіка відправки email
                # наприклад, затримка часу: time.sleep(1)

                # Оновлюємо поле is_sent на True в базі даних
                contact.update(is_sent=True)
                logging.info(f"   ✅ Статус EMAIL для {contact.full_name} оновлено на 'надіслано'.")
            else:
                logging.info(f"   ℹ️ EMAIL для {contact.full_name} вже був надісланий раніше.")
        else:
            logging.error(f"   ❌ Контакт з ID {contact_id} не знайдено в базі даних.")

        # Підтверджуємо, що повідомлення було успішно оброблено
        # Це видаляє повідомлення з черги RabbitMQ
        ch.basic_ack(method.delivery_tag)

    except json.JSONDecodeError:
        logging.error(f"❌ Помилка декодування JSON: {body.decode('utf-8')}")
        ch.basic_ack(method.delivery_tag) # Підтверджуємо, щоб видалити некоректне повідомлення
    except Exception as e:
        logging.error(f"❌ Невідома помилка при обробці повідомлення: {e}")
        logging.error(f"   Повідомлення: {body.decode('utf-8')}")
        # Якщо виникла помилка, можна відхилити повідомлення (basic_nack)
        # або перемістити його в чергу "мертвих листів" (Dead Letter Queue) для подальшого аналізу.
        # Для простоти, поки що підтверджуємо, щоб не заблокувати чергу.
        ch.basic_ack(method.delivery_tag)


# Підключення до RabbitMQ
try:
    connection: pika.BlockingConnection = pika.BlockingConnection(pika.ConnectionParameters(host=rabbit_host))
    channel: pika.adapters.blocking_connection.BlockingChannel = connection.channel()
    logging.info(f"✅ Успішно підключено до RabbitMQ на хості: {rabbit_host}")
except pika.exceptions.AMQPConnectionError as e:
    logging.error(f"❌ Помилка підключення до RabbitMQ: {e}")
    logging.error("Будь ласка, переконайтеся, що RabbitMQ сервер запущений (наприклад, через Docker).")
    sys.exit(1)

# Оголошення черги (повинна бути такою ж, як і в producer)
channel.queue_declare(queue=email_queue_name, durable=True)

# Вказуємо RabbitMQ, що цей consumer буде отримувати повідомлення з даної черги
# on_message_callback: функція, яка буде викликана при отриманні повідомлення
# auto_ack=False: ми будемо вручну підтверджувати обробку повідомлення (ch.basic_ack)
# Це краще, ніж auto_ack=True, бо гарантує, що повідомлення не загубиться,
# якщо обробка завершиться помилкою до підтвердження.
channel.basic_consume(queue=email_queue_name, on_message_callback=callback, auto_ack=False)

logging.info(f"\n[*] Очікування EMAIL повідомлень з черги '{email_queue_name}'. Для виходу натисніть CTRL+C")
# Запускаємо нескінченний цикл, який чекає на повідомлення
channel.start_consuming()
