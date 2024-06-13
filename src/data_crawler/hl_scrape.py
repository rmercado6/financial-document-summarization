import asyncio

from logging import getLogger
from httpx import AsyncClient

from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.constants import DATA_SRC_URLS, HTTP_CLIENT_CONFIG, LOGGER_NAME


logger = getLogger(LOGGER_NAME)


async def scrape_hl_index_stocks_table(url: str, n_pages: int = 6) -> list[dict[str, any]]:
    """Function to scrape stocks table from HL Stocks Table page

    :param url: HL Stocks Table URL
    :param n_pages: Number of pages to scrape from HL Stocks Table page
    """
    logger.debug(f'Scraping HL stocks table from {url}')
    __stocks = {}
    try:
        client = AsyncClient(**HTTP_CLIENT_CONFIG)
        pages = [client.get(url + f"?page={page_number}") for page_number in range(1, n_pages + 1)]
        for response in asyncio.as_completed(pages):
            response = await response
            if response.status_code == 200:
                data = parse_stocks_table(response.text)
                __stocks.update(data)
        logger.debug(f'Finished scraping HL stocks table.')
        return [
            {
                'metadata': {
                    'url_append': DATA_SRC_URLS['hl-financial-statement-and-reports']
                },
                'method': 'GET',
                'url': DATA_SRC_URLS['hl-base'] + url,
                'consumer': parse_financial_statements_and_reports
            }
            for url in __stocks.values()
        ]
    except Exception as e:
        logger.error(f'Error scraping the HL stocks table from {url}.\n\t{e}')
        raise e
