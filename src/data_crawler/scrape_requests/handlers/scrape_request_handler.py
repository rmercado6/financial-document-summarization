import logging
import asyncio

from pathlib import Path

from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME, HTTP_CLIENT_CONFIG, NO_REQUEST_CONSUMERS, NO_RESPONSE_CONSUMERS
from src.data_crawler.scrape_requests.handlers.producers import ScrapeRequestsProducer
from src.data_crawler.scrape_requests.handlers.consumers import ScrapeRequestConsumer, ScrapeResponseConsumer


logger = logging.getLogger(LOGGER_NAME)


async def scrape_request_handler(
        requests: list[dict[str, any]],
        client: AsyncClient = AsyncClient(**HTTP_CLIENT_CONFIG),     # Async HTTP Client
        task_queue: asyncio.Queue = None,     # Queue for ScrapeRequest objects
        response_queue: asyncio.Queue = None,  # Queue for ScrapeResponse objects
) -> None:
    """Asynchronous ScrapeRequest Handler

    :param requests: list[dict[str, any]]   List of requests to generate
    :param client: AsyncClient      HTTP Client for managing HTTP requests
    :param task_queue: asyncio.Queue     Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    :return: None
    """
    logger.debug('Start scrape request handler.')

    # Init queues if not provided in kwargs
    if task_queue is None:
        task_queue = asyncio.Queue()
    if response_queue is None:
        response_queue = asyncio.Queue()

    Path('./out/data-crawler').mkdir(parents=True, exist_ok=True)

    # Producer and Consumer generation
    producers = [  # Build and publish in queue the ScrapeRequest for each stock through producers
        asyncio.create_task(ScrapeRequestsProducer(client, task_queue, requests, _)())
        for _ in range(3)
    ]
    logger.debug('Generated producers for ScrapeRequest object generation.')

    request_consumers = [  # Generate consumers to process the ScrapeRequest objects
        asyncio.create_task(ScrapeRequestConsumer(client, task_queue, response_queue, _)())
        for _ in range(NO_REQUEST_CONSUMERS)
    ]
    logger.debug('Generated consumers for ScrapeRequest object processing.')

    response_consumers = [  # Generate consumers to process the ScrapeRequest objects
        asyncio.create_task(ScrapeResponseConsumer(client, task_queue, response_queue, _)())
        for _ in range(NO_RESPONSE_CONSUMERS)
    ]
    logger.debug('Generated consumers for ScrapeResponse object processing.')

    # Wait for producers and consumers to finish their processes
    await asyncio.gather(*producers)  # wait for producers to finish

    await task_queue.join()  # Wait for consumers to finish and stop them
    [_.cancel() for _ in request_consumers]

    await response_queue.join()  # Wait for consumers to finish and stop them
    [_.cancel() for _ in response_consumers]

    logger.debug('Finished scrape request handler.')
    return None
