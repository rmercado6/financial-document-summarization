import logging
import asyncio

import jsonlines

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.constants import LOGGER_NAME, MAX_RETRIES
from src.data_crawler.scrape_requests.handlers import AsyncTask

logger = logging.getLogger(LOGGER_NAME)

writer_lock = asyncio.Lock()


async def handle_consumer_exception(
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
        async_task.warning(f'Error consuming {type(scrape_object).__name__} {scrape_object.url}')

        # Log error to file
        async with writer_lock:
            try:
                with jsonlines.open('./out/data-crawler/error.jsonl', 'a') as _:
                    _.write(scrape_object.get_postmortem_log(exception))
            except Exception as e:
                async_task.exception(e)

        # Reset
        if scrape_object.reset(async_task.client) < MAX_RETRIES:
            if type(scrape_object) is ScrapeRequest:
                await async_task.task_queue.put(scrape_object)
            elif type(scrape_object) is ScrapeResponse:
                await async_task.response_queue.put(scrape_object)
        if type(scrape_object) is ScrapeRequest:
            async_task.task_queue.task_done()
        elif type(scrape_object) is ScrapeResponse:
            async_task.response_queue.task_done()

    else:
        async_task.warning(f'Error attempting to get {type(scrape_object).__name__} from queue.')

    async_task.exception(exception)
