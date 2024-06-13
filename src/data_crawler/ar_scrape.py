from logging import getLogger

from httpx import Client

from src.data_crawler.constants import LOGGER_NAME, HTTP_CLIENT_CONFIG
from src.data_crawler.ar_parse import parse_stocks_table


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
        if response.status_code == 200:
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
    return None
