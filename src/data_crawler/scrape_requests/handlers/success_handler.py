import logging
import asyncio

import httpx

from src.data_crawler.scrape_requests import ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


async def success_handler(
        response: ScrapeResponse,
        queue: asyncio.Queue,
        response_queue: asyncio.Queue,
        client: httpx.AsyncClient
) -> None:
    """Scrape http successful request response handler

    :param response: ScrapeRequest item
    :param queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue Scrape Response queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    logger.debug(f'Successful request from queue: {response.url}. '
                 f'Sending request to consumer function {response.consumer.__name__}.')

    response.consume(client=client)
    logger.debug(f'Got response from consumer function.')

    await response_queue.put(response)
    if response.further_requests:
        logger.debug(f'Adding {len(response.further_requests)} requests to request queue with '
                     f'actual qsize {queue.qsize()}.')
        [await queue.put(request) for request in response.further_requests]
        logger.debug(f'Added {len(response.further_requests)} requests to request queue with '
                     f'updated qsize {queue.qsize()}.')

