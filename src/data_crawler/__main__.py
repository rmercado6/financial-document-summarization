import asyncio

from httpx import AsyncClient

from src.data_crawler.reuqests import request_producer, request_consumer
from src.data_crawler.hl_index_parser import parse_stocks_table, parse_financial_statements_and_reports
from constants import DATA_SRC_URLS, N_PAGES, HTTP_CLIENT_CONFIG


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
    __stocks_url_queue = list(stocks.values()).copy()
    queue = asyncio.Queue()
    client = AsyncClient(**HTTP_CLIENT_CONFIG)

    requests = [
        {
            'metadata': {
                'url_append': DATA_SRC_URLS['hl-financial-statement-and-reports']
            },
            'method': 'GET',
            'url': DATA_SRC_URLS['hl-base'] + url
        }
        for url in stocks.values()
    ]

    producers = [asyncio.create_task(request_producer(client, queue, requests)) for _ in range(3)]
    consumers = [asyncio.create_task(request_consumer(client, queue, parse_financial_statements_and_reports)) for _ in range(10)]

    await asyncio.gather(*producers)
    print(' --- finish request producing ---')

    await queue.join()

    [c.cancel() for c in consumers]


if __name__ == '__main__':
    stocks = asyncio.run(
        scrape_hl_index_stocks_table(DATA_SRC_URLS['hl-base'] + DATA_SRC_URLS['hl-ftse-all=share-index'], N_PAGES)
    )
    first_stock = list(stocks.keys())[0]
    scraped_data = asyncio.run(scrape_hl_index_stock_pages({first_stock: stocks[first_stock]}))
    print('Done')


