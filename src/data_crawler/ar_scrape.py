import asyncio

from logging import getLogger
from httpx import Client, AsyncClient

from src.data_crawler.constants import LOGGER_NAME, HTTP_CLIENT_CONFIG, ASYNC_AWAIT_TIMEOUT, DATA_SRC_URLS
from src.data_crawler.ar_parse import parse_stocks_table, parse_firms_detail_page
from src.data_crawler.requests import scrape_request_producer, scrape_request_consumer


logger = getLogger(LOGGER_NAME)


def scrape_ar_stocks_table(url: str) -> dict[str, str]:
    """Function to scrape stocks table from AnnualReports Stocks Table page

    :param url: AnnualReports FTSE ALL-SHARE Stocks Table URL
    """
    logger.debug(f'Scraping AR stocks table from {url}')
    __stocks: dict = {}
    try:
        client = Client(**HTTP_CLIENT_CONFIG)
        response = client.get(url)
        if response.is_success:
            __stocks = parse_stocks_table(response.text)
        logger.debug('Finished scraping AR stocks table')
        return __stocks
    except Exception as e:
        logger.error(f"Error scraping the AR stocks table from {url}:\n\t{e}")
        raise e


async def scrape_ar_stock_pages(stocks: dict[str, str]) -> None:
    """Function to scrape stocks pages from AnnualReports

    :param stocks: dict containing stocks urls from stocks table
    """
    logger.debug(f'Starting HL stock pages scraping for {len(stocks.keys())} stocks.')
    async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
        queue = asyncio.Queue()  # Queue for ScrapeRequest objects
        responses = asyncio.Queue()  # Queue for ScrapeResponse objects
        client = AsyncClient(**HTTP_CLIENT_CONFIG)  # Async HTTP Client

        # Build the ScrapeRequest data for each stock
        requests = [
            {
                'metadata': {},
                'method': 'GET',
                'url': DATA_SRC_URLS['hl-base'] + url,
                'consumer': parse_firms_detail_page
            }
            for url in stocks.values()
        ]

        # Producer and Consumer generation
        producers = [  # Build and publish in queue the ScrapeRequest for each stock through producers
            asyncio.create_task(scrape_request_producer(client, queue, requests))
            for _ in range(3)
        ]
        logger.debug('Generated producers for ScrapeRequest object generation.')

        consumers = [  # Generate consumers to process the ScrapeRequest objects
            asyncio.create_task(scrape_request_consumer(client, queue, responses))
            for _ in range(10)
        ]
        logger.debug('Generated consumers for ScrapeRequest object processing.')

        # Wait for producers and consumers to finish their processes
        await asyncio.gather(*producers)  # wait for producers to finish

        await queue.join()  # Wait for consumers to finish and stop them
        [c.cancel() for c in consumers]

        logger.info('Finished scraping AR Index stocks pages.')
    return None
