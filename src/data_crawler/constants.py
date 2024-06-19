import httpx
from logging import INFO, DEBUG


# Number of pages to scrape from HL stocks table
N_PAGES = 6

# dictionary of urls to scrape
DATA_SRC_URLS = {
    'hl-base': 'https://www.hl.co.uk',
    'hl-ftse-all-share-index': '/shares/stock-market-summary/ftse-all-share',
    'hl-financial-statement-and-reports': '/financial-statements-and-reports',
    'ar-base': 'https://www.annualreports.com',
    'ar-ftse-all-share-index': '/Companies?exch=9',
}

# HTTP Client configuration
HTTP_CLIENT_CONFIG = {
    "timeout": httpx.Timeout(60.0),
    "headers": {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    },
    "follow_redirects": False,
}


# Async await Timeout limit
ASYNC_AWAIT_TIMEOUT = 60

# Sleep time between actions for every consumer
CONSUMER_SLEEP_TIME = 10

# Number of ScrapeRequest Consumers
NO_REQUEST_CONSUMERS = 10

# Number of ScrapeResponse Consumers
NO_RESPONSE_CONSUMERS = 10

# Maximum number of request attempts
MAX_RETRIES = 3

# ID for the logger
LOGGER_NAME = 'data-crawler'

# Logging configuration
LOGGING_CONFIG = {
    'prod': {
        'format': '{asctime} - [{levelname:.3}]: {name:>12.12} | {filename:>15.15} [{lineno:4}] | {message}',
        'style': '{',
        'level': INFO
    },
    'testing': {
        'format': '{asctime} - [{levelname:.3}]: {name:>12.12} | {filename:>15.15} [{lineno:4}] | {message}',
        'style': '{',
        'level': DEBUG
    }
}
