import logging
import asyncio

import httpx

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def success_handler(
        scrape_request: ScrapeRequest,
        queue: asyncio.Queue,
        response_queue: asyncio.Queue,
        client: httpx.AsyncClient
) -> None:
    """Scrape http successful request response handler

    :param scrape_request: ScrapeRequest item
    :param queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue Scrape Response queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    logger.debug(f'Successful request from queue: {scrape_request.url}. '
                 f'Sending request to consumer function {scrape_request.consumer.__name__}.')

    response: ScrapeResponse = scrape_request.consumer(scrape_request, client=client)

    logger.debug(f'Got response from consumer function.')
    await response_queue.put(response)
    if response.further_requests:
        logger.debug(f'Adding {len(response.further_requests)} requests to request queue with '
                     f'actual qsize {queue.qsize()}.')
        [await queue.put(request) for request in response.further_requests]
        logger.debug(f'Added {len(response.further_requests)} requests to request queue with '
                     f'updated qsize {queue.qsize()}.')

