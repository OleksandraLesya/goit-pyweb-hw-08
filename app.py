from flask import Flask, render_template, request, redirect, url_for
import logging  # Імпортуємо модуль логування
from typing import List, Optional  # Імпортуємо типи для анотацій

from models import Contact  # Імпортуємо модель Contact
import connect  # noqa: Цей імпорт нашого connect.py ініціалізує підключення до MongoDB Atlas

# Налаштування логування для Flask-додатку
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

app = Flask(__name__)

# Підключення до MongoDB Atlas вже ініціалізовано при імпорті connect.py.
# Ми можемо додати лог-повідомлення, щоб підтвердити, що підключення відбулося.
logging.info("Flask-додаток ініціалізовано. Підключення до MongoDB Atlas встановлено через connect.py.")


@app.route('/')
def index() -> str:
    """
    Головна сторінка веб-додатку, що відображає всі контакти, відсортовані за статусом is_sent.
    """
    logging.info("Запит до головної сторінки '/'")
    # Отримати всі контакти, сортування за is_sent (False спочатку, потім True)
    contacts: List[Contact] = Contact.objects().order_by('is_sent')
    return render_template('index.html', contacts=contacts)


@app.route('/filter', methods=['GET'])
def filter_contacts() -> str:
    """
    Сторінка для фільтрації контактів за статусом is_sent.
    Приймає параметр 'sent' ('true' або 'false').
    """
    logging.info(f"Запит до сторінки фільтрації '/filter' з параметрами: {request.args}")
    sent_param: Optional[str] = request.args.get('sent')

    contacts: List[Contact]
    if sent_param == 'true':
        contacts = Contact.objects(is_sent=True)
        logging.info("Фільтрація контактів: відображено лише відправлені.")
    elif sent_param == 'false':
        contacts = Contact.objects(is_sent=False)
        logging.info("Фільтрація контактів: відображено лише невідправлені.")
    else:
        # Якщо параметр некоректний або відсутній, перенаправляємо на головну сторінку
        logging.warning(f"Некоректний параметр фільтрації 'sent': {sent_param}. Перенаправлення на головну сторінку.")
        return redirect(url_for('index'))

    return render_template('index.html', contacts=contacts)


if __name__ == '__main__':
    logging.info("Запуск Flask-додатку...")
    app.run(debug=True)

