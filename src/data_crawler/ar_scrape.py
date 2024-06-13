from logging import getLogger

from src.data_crawler.constants import LOGGER_NAME


logger = getLogger(LOGGER_NAME)


def scrape_ar_stocks_table(url: str) -> dict[str, str]:
    """Function to scrape stocks table from AnnualReports Stocks Table page

    :param url: AnnualReports FTSE ALL-SHARE Stocks Table URL
    """
    return {}


async def scrape_ar_stock_pages(stocks: dict[str, str]) -> None:
    """Function to scrape stocks pages from AnnualReports

    :param stocks: dict containing stocks urls from stocks table
    """
    return None
