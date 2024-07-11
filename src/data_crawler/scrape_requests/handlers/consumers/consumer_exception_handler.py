import logging
import asyncio

import httpx
import jsonlines

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME, MAX_RETRIES


logger = logging.getLogger(LOGGER_NAME)


async def consumer_exception_handler(
        exception: Exception,
        scrape_object: ScrapeRequest or ScrapeResponse,
        task_queue: asyncio.Queue,
        response_queue: asyncio,
        client: httpx.AsyncClient,
) -> None:
    """Scrape request consumer exception handler

    :param response_queue:
    :param exception: Exception to be handled
    :param scrape_object: ScrapeRequest item
    :param task_queue: asyncio.Queue Scrape Request queue
    :param client: AsyncClient HTTP Client for managing HTTP requests
    """
    if scrape_object is not None:
        logger.warning('Error consuming ScrapeRequest %s', scrape_object.url)
        # Log error to file
        with jsonlines.open('./out/data-crawler/error.jsonl', 'a') as _:
            _.write(scrape_object.get_postmortem_log())
        if scrape_object.reset(client) < MAX_RETRIES:
            if scrape_object is ScrapeRequest:
                await task_queue.put(scrape_object)
            elif scrape_object is ScrapeResponse:
                await response_queue.put(scrape_object)
    else:
        logger.warning('Error attempting to get ScrapeRequest from queue.')
        raise exception

    logger.exception(exception)
    task_queue.task_done()

