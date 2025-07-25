# Message Queue and Database Integration Project

This project demonstrates a hybrid architecture integrating:
- MongoDB Atlas (cloud-based NoSQL database) for storing quotes, authors, and contacts.
- RabbitMQ (via Docker) as a message broker for asynchronous message processing (email and SMS).
- Redis (via Docker) for caching CLI query results and improving performance.
- Flask web interface for displaying and filtering contacts.
It includes a CLI application for querying data and a producer/consumer system for message processing.

The system includes:
- A CLI application to search quotes (with Redis-based caching and autocomplete).
- A producer that creates fake contact messages and sends them to RabbitMQ queues.
- Two consumers that simulate sending messages via email and SMS (from separate queues).
- A web UI for viewing and filtering contacts.


## Project Structure

├── app.py              # Flask web application for displaying data and filtering contacts
├── cache.py            # Redis caching utilities
├── config.ini          # Configuration file for MongoDB, RabbitMQ, and Redis
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
├── templates/          # Folder for Flask HTML templates
│   └── index.html      # Template for displaying the contact list
├── static/             # Folder for Flask static files (CSS, JS, images)
│   └── css/            # Folder for CSS files
│       └── styles.css  # Main CSS file for web interface styling
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

This script creates fake contacts and sends messages to the appropriate 
RabbitMQ queues depending on the preferred contact method (email or SMS).

5. In separate terminals, run consumers
Run the consumers in separate terminals to simulate message delivery:
```poetry run python consumer_email.py```
```poetry run python consumer_sms.py```

6. Run CLI Application for Searching
Run the main CLI application:
```poetry run python main.py```

Use commands like:
name:Albert Einstein
tag:life
tags:life,live
name:al (partial matches with autocomplete)
exit to quit
Redis caches results for name: and tag: queries.

7. Run Flask Web UI
```poetry run python app.py```

Then open in browser:
http://127.0.0.1:5000
You’ll see a contact list with filters:
All
Sent
Not sent
Each contact shows name, email, phone, message type, and sending status (sent or pending).


## Features

MongoEngine ODM for MongoDB Atlas (cloud)
Redis for caching quote searches (via CLI)
RabbitMQ (2 queues: email and sms) with separate consumers
Faker-based data generation for contacts
CLI with autocomplete and keyword-based search
Web interface (Flask + Jinja2) for visualizing contacts and delivery status
Docker Compose for Redis and RabbitMQ setup


## Dependencies

Python 3.11+
MongoDB Atlas
MongoEngine
Redis
RabbitMQ + Pika
Faker
Flask + Jinja2
Docker + Docker Compose
Poetry for dependency & virtual environment management
configparser (for reading config.ini)