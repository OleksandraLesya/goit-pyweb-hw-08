# Message Queue and Database Integration Project

This project demonstrates a hybrid architecture integrating:
- MongoDB Atlas (cloud-based database) for data storage.
- RabbitMQ (local, via Docker) as a message broker for asynchronous email/SMS sending.
- Redis (local, via Docker) for caching in the CLI application. 

It includes a CLI application for querying data and a producer/consumer system for message processing.

## Project Structure

├── cache.py            # Redis caching utilities
├── config.ini          # Configuration file for MongoDB and RabbitMQ
├── connect.py          # Establishes connection to MongoDB Atlas
├── docker-compose.yml  # Docker Compose for RabbitMQ and Redis services
├── data/               # Folder containing JSON data files
│   ├── authors.json    # JSON file with author data
│   └── quotes.json     # JSON file with quote data
├── load_data.py        # Script to load initial data (authors, quotes) into MongoDB
├── main.py             # CLI application for searching quotes with Redis caching
├── models.py           # MongoEngine models for Author, Quote, and Contact
├── producer.py         # Generates fake contacts and sends messages to RabbitMQ queues
├── consumer_email.py   # Consumes messages from 'email_messages' queue and simulates email sending
├── consumer_sms.py     # Consumes messages from 'sms_messages' queue and simulates SMS sending
├── README.md           # Project documentation
└── pyproject.toml      # Poetry project configuration


## How to Run Project

1. Start Docker Services (RabbitMQ and Redis):
```docker compose up -d```

2. Install Dependencies:
```poetry install```

3. Load Initial Data (Authors and Quotes):
```poetry run python load_data.py```

4. Run producer to generate contacts and send messages to the queues:
```poetry run python producer.py```

5. In separate terminals, run consumers:
```poetry run python consumer_email.py```
```poetry run python consumer_sms.py```

6. Run CLI Application for Searching
Run the main CLI application:
```poetry run python main.py```

You can then use commands like name:
Albert Einstein, tag:life, tags:life,live, name:al, tag:li, or exit. 
Results for name: and tag: commands will be cached in Redis.


## Dependencies

pika (for RabbitMQ communication)
mongoengine (ODM for MongoDB)
redis (for Redis client)
Faker (for generating fake data)
python-dotenv (if using .env for config, though configparser is used here)
configparser (for reading config.ini)
