import logging
import asyncio

import httpx

from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def redirect_handler(
        scrape_request: ScrapeRequest,
        queue: asyncio.Queue,
        client: httpx.AsyncClient
) -> None:
    """Handle http redirects

    :param scrape_request: ScrapeRequest item
    :param queue: asyncio.Queue Scrape Request queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    logger.info(f'Redirecting request {scrape_request.url} to {scrape_request.response.headers["Location"]}')

    # Build new URL
    url = httpx.URL(scrape_request.response.headers['Location'])
    if not url.host:
        url = httpx.URL(
            scrape_request.response.headers['Location'],
            host=scrape_request.response.request.url.host,
            scheme=scrape_request.response.request.url.scheme
        )
    url = str(url)
    if 'url_append' in scrape_request.metadata.keys():
        url += scrape_request.metadata['url_append']

    # Update metadata with redirect tracking information
    scrape_request.metadata.update({
        'redirected_from': scrape_request.url,
        'url': url
    })

    # Add new request to queue
    await queue.put(
        ScrapeRequest(
            metadata=scrape_request.metadata,
            request=client.request(method=scrape_request.request.method, url=url),
            consumer=scrape_request.consumer
        )
    )
