from logging import getLogger

from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.requests import ScrapeRequest, ScrapeResponse


logger = getLogger(LOGGER_NAME)


def parse_stocks_table(response_text: str) -> dict[str, str]:
    """Function to parse the stocks table content

    :param response_text: html response text
    :return: dict[str, str] dictionary with the stock name and the url to the stock data page
    """
    return {}


def parse_firms_detail_page(
        request: ScrapeRequest,
        client: AsyncClient or None = None
) -> ScrapeResponse:
    """Functon to parse the firm's detail page to get the financial reports pdf download links

    :param request: ScrapeRequest request object.
    :param client: Httpx AsyncClient HTTP Client to manage HTTP requests.
    :return: None
    """
    requests = []   # Add the request for each of teh files to download
    return ScrapeResponse({}, None, requests)

