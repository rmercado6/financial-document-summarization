import logging
import asyncio

import httpx

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def redirect_handler(
        response: ScrapeResponse,
        queue: asyncio.Queue,
        client: httpx.AsyncClient
) -> None:
    """Handle http redirects

    :param response: ScrapeRequest item
    :param queue: asyncio.Queue Scrape Request queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    logger.info(f'Redirecting request {response.url} to {response.headers["Location"]}')

    # Build new URL
    url = httpx.URL(response.headers['Location'])
    if not url.host:
        url = httpx.URL(
            response.headers['Location'],
            host=response.host,
            scheme=response.scheme
        )
    url = str(url)
    if 'url_append' in response.metadata.keys():
        url += response.metadata['url_append']

    # Update metadata with redirect tracking information
    response.metadata.update({
        'redirected_from': response.url,
        'url': url
    })

    # Add new request to queue
    await queue.put(
        ScrapeRequest(
            metadata=response.metadata.copy(),
            request=client.request(method=response.method, url=url),
            consumer=response.consumer
        )
    )
