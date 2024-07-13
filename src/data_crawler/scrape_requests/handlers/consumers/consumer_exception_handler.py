import logging
import asyncio

import jsonlines

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME, MAX_RETRIES
from src.data_crawler.scrape_requests.handlers import AsyncTask

logger = logging.getLogger(LOGGER_NAME)

writer_lock = asyncio.Lock()


async def consumer_exception_handler(
        exception: Exception,
        scrape_object: ScrapeRequest or ScrapeResponse,
        async_task: AsyncTask
) -> None:
    """Scrape request consumer exception handler

    :param exception: Exception to be handled
    :param scrape_object: ScrapeRequest item
    :param async_task: AsyncTask object where the exception was raised
    """
    if scrape_object is not None:
        async_task.warning(f'Error consuming ScrapeRequest {scrape_object.url}')

        # Log error to file
        async with writer_lock:
            with jsonlines.open('./out/data-crawler/error.jsonl', 'a') as _:
                _.write(scrape_object.get_postmortem_log())

        if scrape_object.reset(async_task.client) < MAX_RETRIES:
            if scrape_object is ScrapeRequest:
                await async_task.task_queue.put(scrape_object)
            elif scrape_object is ScrapeResponse:
                await async_task.response_queue.put(scrape_object)
    else:
        async_task.warning('Error attempting to get ScrapeRequest from queue.')
        raise exception

    async_task.exception(exception)
    async_task.task_queue.task_done()

