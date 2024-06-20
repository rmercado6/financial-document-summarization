from logging import getLogger
from httpx import Client

from src.data_crawler.constants import LOGGER_NAME, HTTP_CLIENT_CONFIG, DATA_SRC_URLS
from src.data_crawler.ar_parse import parse_stocks_table, parse_firms_detail_page


logger = getLogger(LOGGER_NAME)


def scrape_ar_stocks_table(url: str) -> list[dict[str, any]]:
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
        return [
            {
                'metadata': {
                    'url': DATA_SRC_URLS['ar-base'] + url,
                    'method': 'GET'
                },
                'method': 'GET',
                'url': DATA_SRC_URLS['ar-base'] + url,
                'consumer': parse_firms_detail_page
            }
            for url in __stocks.values()
        ]
    except Exception as e:
        logger.error(f"Error scraping the AR stocks table from {url}:\n\t{e}")
        raise e
