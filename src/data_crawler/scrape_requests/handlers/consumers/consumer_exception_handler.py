import logging
import asyncio

import httpx
import jsonlines

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME, MAX_RETRIES


logger = logging.getLogger(LOGGER_NAME)


async def consumer_exception_handler(
        exception: Exception,
        scrape_request: ScrapeRequest,
        queue: asyncio.Queue,
        client: httpx.AsyncClient
) -> None:
    """Scrape request consumer exception handler

    :param exception: Exception to be handled
    :param scrape_request: ScrapeRequest item
    :param queue: asyncio.Queue Scrape Request queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    if scrape_request is not None:
        logger.warning('Error consuming ScrapeRequest %s', scrape_request.url)
        # Log error to file
        with jsonlines.open('./out/data-crawler/error.jsonl', 'a') as _:
            _.write(scrape_request.get_postmortem_log())
        if scrape_request.reset(client) < MAX_RETRIES:
            await queue.put(scrape_request)
    else:
        logger.warning('Error attempting to get ScrapeRequest from queue.')
        raise exception

    logger.exception(exception)
    queue.task_done()

