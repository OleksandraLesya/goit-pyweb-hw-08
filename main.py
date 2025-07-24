import sys
import json
import logging # Import the logging module
from typing import List, Dict, Any, Optional # Import types for annotations
import re # Import regex for pattern matching

from models import Author, Quote # Import models
from connect import connect_db # Import the function for connecting to the DB
from cache import get_cache, set_cache # Import caching functions

# Configure logging for this module
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def search_quotes_cli() -> None:
    """
    Function to run the CLI application for searching quotes with Redis caching support.
    Allows searching quotes by author name, single tag, or multiple tags.
    Added support for shortened search values using regular expressions.
    """
    # 1. Connect to the MongoDB Atlas database
    # The connect_db() function already outputs a message about successful connection or error.
    connect_db()

    logging.info("\nПідключено до бази даних. Введіть команду для пошуку (наприклад, 'name: Albert Einstein', 'tag: life', 'tags: humor,funny') або 'exit' для виходу.")
    logging.info("Результати з кешу Redis будуть позначені '>>> From Redis:', з MongoDB - '>>> From MongoDB:'.")
    logging.info("Тепер також підтримується скорочений пошук, наприклад, 'name: al' або 'tag: li'.")

    while True:
        user_input: str = input(">>> ").strip() # Get user input
        if user_input.lower() == 'exit':
            logging.info("Вихід з програми.")
            break # Exit the loop if the user entered 'exit'

        if ":" not in user_input:
            logging.warning("Некоректний формат. Використовуйте 'name: [ім'я]', 'tag: [тег]', 'tags: [тег1],[тег2]' або 'exit'.")
            continue

        key: str
        value: str
        try:
            key, value = user_input.split(":", 1)
        except ValueError:
            logging.warning("Некоректний формат команди. Будь ласка, використовуйте 'команда: значення'.")
            continue

        key = key.strip().lower() # Convert key to lowercase for convenience
        value = value.strip()

        if not value:
            logging.warning(f"Будь ласка, вкажіть значення для '{key}'.")
            continue

        # Form the key for Redis cache
        cache_key: str = f"{key}:{value}"

        # 1. Try to get data from Redis cache
        cached_result: Optional[List[Dict[str, Any]]] = get_cache(cache_key)
        if cached_result:
            logging.info("\n>>> From Redis:")
            # Output cached results
            for item in cached_result:
                logging.info(f"- \"{item['quote']}\" - {item['author']} (Теги: {', '.join(item['tags'])})")
            continue # Go to the next loop iteration if data is found in cache

        # 2. If no data in cache, search in MongoDB
        logging.info("\n>>> From MongoDB:")
        quotes_from_db: List[Dict[str, Any]] = [] # List to store results from DB

        if key == "name":
            # Use __iregex for case-insensitive search by part of the name (starts with)
            # The regex pattern is now more robust to ensure it matches the beginning of the string
            authors = Author.objects(fullname__iregex=f"^{re.escape(value)}")
            if authors:
                for author in authors:
                    quotes = Quote.objects(author=author)
                    if quotes:
                        for q in quotes:
                            quotes_from_db.append({
                                "quote": q.quote,
                                "author": q.author.fullname,
                                "tags": q.tags
                            })
            if not quotes_from_db: # If nothing was found after iterating through authors
                logging.info(f"Цитат від автора, ім'я якого починається з '{value}', не знайдено.")


        elif key == "tag":
            # Use __iregex for case-insensitive search by part of the tag (starts with)
            quotes = Quote.objects(tags__iregex=f"^{re.escape(value)}")
            if quotes:
                for q in quotes:
                    quotes_from_db.append({
                        "quote": q.quote,
                        "author": q.author.fullname,
                        "tags": q.tags
                    })
            else:
                logging.info(f"Цитат з тегом, що починається з '{value}', не знайдено.")

        elif key == "tags":
            tags_list: List[str] = [t.strip() for t in value.split(',') if t.strip()]
            if not tags_list:
                logging.warning("Будь ласка, вкажіть дійсні теги.")
                continue
            # Use __all for searching quotes that contain ALL specified tags
            quotes = Quote.objects(tags__all=tags_list)
            if quotes:
                for q in quotes:
                    quotes_from_db.append({
                        "quote": q.quote,
                        "author": q.author.fullname,
                        "tags": q.tags
                    })
            else:
                logging.info(f"Цитат з тегами '{', '.join(tags_list)}' не знайдено.")
        else:
            logging.warning("Невідома команда.")
            continue # Go to the next loop iteration

        # 3. If data was found in MongoDB, save it to Redis cache
        if quotes_from_db:
            set_cache(cache_key, quotes_from_db) # Save list of dictionaries
            # Output results obtained from MongoDB
            for item in quotes_from_db:
                logging.info(f"- \"{item['quote']}\" - {item['author']} (Теги: {', '.join(item['tags'])})")
        elif not cached_result: # If nothing was in cache and nothing found in DB
            logging.info("Нічого не знайдено за вашим запитом.")


# Run the CLI application if the script is run directly
if __name__ == "__main__":
    search_quotes_cli()
