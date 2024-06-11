import asyncio

from httpx import AsyncClient

from src.data_crawler.requests import scrape_request_producer, scrape_request_consumer
from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.constants import DATA_SRC_URLS, HTTP_CLIENT_CONFIG, ASYNC_AWAIT_TIMEOUT


async def scrape_hl_index_stocks_table(url: str, n_pages: int = 6) -> dict[str, str]:
    """Function to scrape stocks table from HL Stocks Table page

    :param url: HL Stocks Table URL
    :param n_pages: Number of pages to scrape from HL Stocks Table page
    """
    __stocks = {}
    try:
        client = AsyncClient(**HTTP_CLIENT_CONFIG)
        pages = [client.get(url + f"?page={page_number}") for page_number in range(1, n_pages + 1)]
        for response in asyncio.as_completed(pages):
            response = await response
            if response.status_code == 200:
                data = parse_stocks_table(response.text)
                __stocks.update(data)
        return __stocks
    except Exception as e:
        raise e


async def scrape_hl_index_stock_pages(stocks: dict[str, str]) -> None:
    """Function to scrape stocks pages from HL

    :param stocks: dict containing stocks urls from stocks table
    """
    async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
        queue = asyncio.Queue()
        responses = asyncio.Queue()
        client = AsyncClient(**HTTP_CLIENT_CONFIG)

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

        producers = [asyncio.create_task(scrape_request_producer(client, queue, requests)) for _ in range(3)]
        consumers = [
            asyncio.create_task(scrape_request_consumer(client, queue, responses))
            for _ in range(10)
        ]

        await asyncio.gather(*producers)
        await queue.join()

        [c.cancel() for c in consumers]
