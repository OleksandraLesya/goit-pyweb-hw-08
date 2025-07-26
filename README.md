# Message Queue and Database Integration Project

This project demonstrates a hybrid architecture integrating:
- MongoDB Atlas (cloud-based NoSQL database) for storing quotes, authors, and contacts.
- RabbitMQ (via Docker) as a message broker for asynchronous message processing (email and SMS).
- Redis (via Docker) for caching CLI query results and improving performance.
- Flask web interface for displaying and filtering contacts.
It includes a CLI application for querying data and a producer/consumer system for message processing.
- Scrapy crawler for scraping quote and author data from http://quotes.toscrape.com and storing into MongoDB.

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
├── main.py             # Main entry point: CLI application for searching quotes 
                            with Redis caching, and also for launching Scrapy
├── models.py           # MongoEngine models for Author, Quote, and Contact
├── producer.py         # Generates fake contacts and sends messages to RabbitMQ queues
├── consumer_email.py   # Consumes messages from 'email_messages' queue and simulates email sending
├── consumer_sms.py     # Consumes messages from 'sms_messages' queue and simulates SMS sending
├── scraper/
│   ├── scrapy.cfg
│   ├── __init__.py
│   ├── items.py          # Item definitions for Scrapy
│   ├── pipelines.py      # Optional: logic for MongoDB integration
│   ├── settings.py       # Scrapy project settings
│   └── spiders/
        ├── __init__.py
│       └── quotes.py  # Spider that scrapes quotes.toscrape.com
├── run_scraper.py         # Script to run Scrapy programmatically
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

3. Run producer to generate contacts and send messages to the queues:
```poetry run python producer.py```

This script creates fake contacts and sends messages to the appropriate 
RabbitMQ queues depending on the preferred contact method (email or SMS).

4. In separate terminals, run consumers
Run the consumers in separate terminals to simulate message delivery:
```poetry run python consumer_email.py```
```poetry run python consumer_sms.py```

6. Scrape and Load Data (Quotes and Authors):
This step collects fresh data from the web and populates your MongoDB.
`poetry run python main.py`

When prompted, select **option 1** to "Запустити Scrapy (збір даних)".
This will:

- Crawl all pages on http://quotes.toscrape.com.
- Extract authors and quotes.
- Save them to data/authors.json (de-duplicated by Pipeline) and data/quotes.json.
- After scraping, run the load_data.py script to upload these JSON files into your MongoDB Atlas.

7. Run CLI Application for Searching:
`poetry run python main.py`

When prompted, select **option 2** to "Запустити CLI-додаток (пошук цитат)".
Use commands like:

- name:Albert Einstein
- tag:life
- tags:life,live
- name:al (for partial matches with autocomplete)
- exit to quit
- Redis caches results for name: and tag: queries.

8. Run Flask Web UI
```poetry run python app.py```

Then open in browser:
http://127.0.0.1:5000
You’ll see a contact list with filters:
- All
- Sent
- Not sent
Each contact shows name, email, phone, message type, and sending status (sent or pending).


## Features

1. [x] MongoEngine ODM for MongoDB Atlas (cloud)
2. [x] Redis for caching quote searches (via CLI)
3. [x] RabbitMQ (2 queues: email and sms) with separate consumers
4. [x] Scrapy crawler for automated data scraping, integrated into main.py
5. [x] Faker-based data generation for contacts
6. [x] CLI with autocomplete and keyword-based search
7. [x] Web interface (Flask + Jinja2) for visualizing contacts and delivery status
8. [x] Docker Compose for Redis and RabbitMQ setup


## Dependencies

* Python 3.11+
* MongoDB Atlas
* MongoEngine
* Redis
* RabbitMQ + Pika
* Faker
* Flask + Jinja2
* Docker + Docker Compose
* Poetry for dependency & virtual environment management
* configparser (for reading config.ini)