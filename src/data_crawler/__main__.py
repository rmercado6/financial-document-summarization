import asyncio

from httpx import AsyncClient

from src.data_crawler.hl_index_parser import parse_stocks_table, parse_financial_statements_and_reports
from constants import BASE_URLS, N_PAGES, CLIENT_HEADERS


async def scrape_hl_index_stocks_table(url: str, n_pages: int = 6) -> dict[str, str]:
    __stocks = {}
    try:
        pages = [
            AsyncClient(headers=CLIENT_HEADERS).get(url + f"?page={page_number}")
            for page_number in range(1, n_pages + 1)
        ]
        for response in asyncio.as_completed(pages):
            response = await response
            if response.status_code == 200:
                data = parse_stocks_table(response.text)
                __stocks.update(data)
        return __stocks
    except Exception as e:
        raise e


async def scrape_hl_index_stock_page(_stocks: dict[str, str]):
    try:
        pages = [
            AsyncClient(headers=CLIENT_HEADERS).get(s + '/financial-statements-and-reports')
            for s in _stocks.values()
        ]
        for response in asyncio.as_completed(pages):
            response = await response
            if response.status_code == 200:
                data = parse_financial_statements_and_reports(response.text)
                _stocks.update(data)
        return _stocks
    except Exception as e:
        raise e


if __name__ == '__main__':
    stocks = asyncio.run(scrape_hl_index_stocks_table(BASE_URLS['hl-index'], N_PAGES))
    print(scrape_hl_index_stock_page(stocks))
    print('Done')
