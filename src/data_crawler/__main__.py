import asyncio

from typing import Callable
from inspect import iscoroutinefunction
from httpx import AsyncClient

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


async def scrape_hl_index_stock_pages(_stocks: dict[str, str]):
    __stocks_url_queue = list(_stocks.values()).copy()
    queue = asyncio.Queue()
    client = AsyncClient(**HTTP_CLIENT_CONFIG)

    async def request_producer(_queue: asyncio.Queue):
        while len(__stocks_url_queue) > 0:
            await _queue.put({
                'metadata': {
                    'url_append': DATA_SRC_URLS['hl-financial-statement-and-reports']
                },
                'request': client.get(DATA_SRC_URLS['hl-base'] + __stocks_url_queue.pop() + DATA_SRC_URLS['hl-financial-statement-and-reports'])
            })

    async def request_consumer(_queue: asyncio.Queue, consumer_function: Callable):
        while True:
            __queue_item = await _queue.get()
            __response = await __queue_item['request']
            if __response.is_redirect:
                print(__response)
                await _queue.put({
                    'request': client.get(
                        __response.headers['Location'] + DATA_SRC_URLS['hl-financial-statement-and-reports']
                    )
                })
            elif __response.is_success:
                print(__response.url)
                if iscoroutinefunction(consumer_function):
                    await consumer_function(__response.text)
                else:
                    consumer_function(__response.text)
            queue.task_done()

    producers = [asyncio.create_task(request_producer(queue)) for _ in range(3)]
    consumers = [asyncio.create_task(request_consumer(queue, parse_financial_statements_and_reports)) for _ in range(10)]

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


