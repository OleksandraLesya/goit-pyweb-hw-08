# models.py
from mongoengine import Document, StringField, EmailField, BooleanField, ReferenceField, ListField, URLField, DateTimeField
import datetime

# Модель для автора
class Author(Document):
    fullname = StringField(required=True, unique=True)
    born_date = StringField()
    born_location = StringField()
    description = StringField()
    meta = {'collection': 'authors'} # Вказуємо назву колекції в MongoDB

# Модель для цитати
class Quote(Document):
    quote = StringField(required=True)
    tags = ListField(StringField())
    author = ReferenceField(Author) # Посилання на модель Author
    meta = {'collection': 'quotes'} # Вказуємо назву колекції в MongoDB

# НОВА МОДЕЛЬ: Contact
class Contact(Document):
    # Повне ім'я контакту
    full_name = StringField(required=True)
    # Email контакту, обов'язкове поле та унікальне
    email = EmailField(required=True, unique=True)
    # Логічне поле, яке вказує, чи було надіслано повідомлення
    # За замовчуванням False (повідомлення не надіслано)
    is_sent = BooleanField(default=False)
    # Додаткове поле: телефонний номер (для додаткового завдання)
    phone_number = StringField(required=False) # Зроблено необов'язковим
    # Додаткове поле: кращий спосіб надсилання повідомлень (email або sms)
    # Буде використовуватися для маршрутизації повідомлень у різні черги
    preferred_channel = StringField(choices=('email', 'sms'), default='email')
    # Додаткове поле для інформаційного навантаження, наприклад, дата створення контакту
    created_at = DateTimeField(default=datetime.datetime.now)

    meta = {'collection': 'contacts'} # Вказуємо назву колекції в MongoDB
