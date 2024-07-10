import logging
import asyncio

from httpx import AsyncClient

from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.scrape_requests.handlers import redirect_handler, success_handler
from src.data_crawler.scrape_requests.handlers.consumers import consumer_exception_handler
from src.data_crawler.constants import LOGGER_NAME, CONSUMER_SLEEP_TIME


logger = logging.getLogger(LOGGER_NAME)


async def scrape_request_consumer(
        client: AsyncClient,
        queue: asyncio.Queue,
        response_queue: asyncio.Queue
) -> None:
    """Scraping Request consumer

    Processes and handles requests through the scraping process.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    :return: None
    """
    logger.debug(f'Starting Request Consumer')
    while True:
        scrape_request: ScrapeRequest or None = None
        try:
            # Get scrape request from queue
            logger.debug('Request Consumer looking on queue for response to handle. qsize: %s', queue.qsize())
            scrape_request = await queue.get()
            logger.debug('Got request from queue[%s]: %s', queue.qsize(), scrape_request)

            # Verify queue item is a compatible Request, remove if not
            if type(scrape_request) is not ScrapeRequest:
                logger.warning(f'Bad request from queue. {type(scrape_request)} object is not a ScrapeRequest object.')
                queue.task_done()
                continue

            # Execute http request
            await scrape_request.send()

            # Process response
            logger.info('Processing Scrape Request %s', scrape_request.url)
            if scrape_request.response.is_redirect:     # Process redirected responses
                await redirect_handler(scrape_request, queue, client)
            elif scrape_request.response.is_success:    # Process successful requests
                await success_handler(scrape_request, queue, response_queue, client)
            else:
                raise Exception(f'Unknown status code {scrape_request.response.status}')

            # Remove processed item from queue
            queue.task_done()
            logger.debug('Task removed from queue.')

        # Handle Exceptions if any
        except Exception as e:
            await consumer_exception_handler(e, scrape_request, queue, client)

        finally:
            if scrape_request is not None:
                logger.info(f'Finished processing request {scrape_request.url}. '
                            f'Request queue: {queue.qsize()}; Response queue: {response_queue.qsize()}')
            logger.debug(f'Request Consumer Released, sleeping...')

            # Sleep consumer for configured amount of time
            await asyncio.sleep(CONSUMER_SLEEP_TIME)
            logger.debug('Resuming Request Consumer.')


