import asyncio

from logging import getLogger
from httpx import AsyncClient

from src.data_crawler.requests import scrape_request_producer, scrape_request_consumer
from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.constants import DATA_SRC_URLS, HTTP_CLIENT_CONFIG, ASYNC_AWAIT_TIMEOUT, LOGGER_NAME


logger = getLogger(LOGGER_NAME)


async def scrape_hl_index_stocks_table(url: str, n_pages: int = 6) -> dict[str, str]:
    """Function to scrape stocks table from HL Stocks Table page

    :param url: HL Stocks Table URL
    :param n_pages: Number of pages to scrape from HL Stocks Table page
    """
    logger.debug(f'Scraping HL Index stocks table from {url}')
    __stocks = {}
    try:
        client = AsyncClient(**HTTP_CLIENT_CONFIG)
        pages = [client.get(url + f"?page={page_number}") for page_number in range(1, n_pages + 1)]
        for response in asyncio.as_completed(pages):
            response = await response
            if response.status_code == 200:
                data = parse_stocks_table(response.text)
                __stocks.update(data)
        logger.debug(f'Finished scraping HL Index stocks table.')
        return __stocks
    except Exception as e:
        logger.error(f'Error scraping the HL Index stocks table. {e}')
        raise e


async def scrape_hl_index_stock_pages(stocks: dict[str, str]) -> None:
    """Function to scrape stocks pages from HL

    :param stocks: dict containing stocks urls from stocks table
    """
    logger.debug(f'Starting HL stock pages scraping for {len(stocks.keys())} stocks.')
    async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
        queue = asyncio.Queue()     # Queue for ScrapeRequest objects
        responses = asyncio.Queue()     # Queue for ScrapeResponse objects
        client = AsyncClient(**HTTP_CLIENT_CONFIG)   # Async HTTP Client

        # Build the ScrapeRequest data for each stock
        requests = [
            {
                'metadata': {
                    'url_append': DATA_SRC_URLS['hl-financial-statement-and-reports']
                },
                'method': 'GET',
                'url': DATA_SRC_URLS['hl-base'] + url,
                'consumer': parse_financial_statements_and_reports
            }
            for url in stocks.values()
        ]

        # Producer and Consumer generation
        producers = [   # Build and publish in queue the ScrapeRequest for each stock through producers
            asyncio.create_task(scrape_request_producer(client, queue, requests))
            for _ in range(3)
        ]
        logger.debug('Generated producers for ScrapeRequest object generation.')

        consumers = [   # Generate consumers to process the ScrapeRequest objects
            asyncio.create_task(scrape_request_consumer(client, queue, responses))
            for _ in range(10)
        ]
        logger.debug('Generated consumers for ScrapeRequest object processing.')

        # Wait for producers and consumers to finish their processes
        await asyncio.gather(*producers)    # wait for producers to finish

        await queue.join()  # Wait for consumers to finish and stop them
        [c.cancel() for c in consumers]

        logger.info('Finished scraping HL Index stocks pages.')

        # TODO: Process responses (insert into non relational DB (Mongo) or write in jsonl file.
