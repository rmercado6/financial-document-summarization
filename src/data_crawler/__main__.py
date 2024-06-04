import asyncio

from httpx import AsyncClient

from src.data_crawler.hl_index_parser import parse_stock_table
from constants import BASE_URLS, N_PAGES
from constants import CLIENT_HEADERS


async def scrape(url: str, n_pages: int = 6) -> dict[str, str]:
    __shares = {}
    try:
        pages = [
            AsyncClient(headers=CLIENT_HEADERS).get(url + f"?page={page_number}")
            for page_number in range(1, n_pages + 1)
        ]
        for response in asyncio.as_completed(pages):
            response = await response
            data = parse_stock_table(response.text)
            __shares.update(data)
        return __shares
    except Exception as error:
        raise error


if __name__ == '__main__':
    shares = asyncio.run(scrape(BASE_URLS['hl-index'], N_PAGES))
    print('Done')
