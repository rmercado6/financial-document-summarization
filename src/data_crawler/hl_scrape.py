import asyncio

from httpx import AsyncClient

from src.data_crawler.requests import request_producer, request_consumer
from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.constants import DATA_SRC_URLS, HTTP_CLIENT_CONFIG


async def scrape_hl_index_stocks_table(url: str, n_pages: int = 6) -> dict[str, str]:
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


async def scrape_hl_index_stock_pages(stocks: dict[str, str]):
    async with asyncio.timeout(5):
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

        producers = [asyncio.create_task(request_producer(client, queue, requests)) for _ in range(3)]
        consumers = [
            asyncio.create_task(request_consumer(client, queue, responses))
            for _ in range(10)
        ]

        await asyncio.gather(*producers)
        await queue.join()

        [c.cancel() for c in consumers]
