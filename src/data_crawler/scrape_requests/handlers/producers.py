import logging
import asyncio

from httpx import AsyncClient

from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def scrape_request_producer(
        client: AsyncClient,
        queue: asyncio.Queue,
        requests: list[dict[str, any]]
) -> None:
    """Initial Scraping Request producer

    Generates ScrapeRequest instances foreach HTTP request in the 'requests' list.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param requests: list[dict[str, any]]   List of requests to generate
    :return: None
    """
    while len(requests) > 0:
        r = requests.pop()
        url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
        logger.debug('Producing %s request: %s', r['method'], r['url'])
        r['metadata']['url'] = url
        await queue.put(
            ScrapeRequest(
                metadata=r['metadata'],
                request=client.request(method=r['method'], url=url),
                consumer=r['consumer']
            )
        )

