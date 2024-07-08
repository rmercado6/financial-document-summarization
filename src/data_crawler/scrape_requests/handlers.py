import asyncio
import logging
import httpx
import jsonlines

from pathlib import Path
from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.constants import (HTTP_CLIENT_CONFIG, CONSUMER_SLEEP_TIME, NO_REQUEST_CONSUMERS,
                                        NO_RESPONSE_CONSUMERS, MAX_RETRIES)
from src.data_crawler.scrape_requests.requests import ScrapeRequest, ScrapeResponse


logger = logging.getLogger(LOGGER_NAME)


async def scrape_request_producer(
        client: AsyncClient,
        queue: asyncio.Queue,
        requests: list[dict[str, any]]
) -> None:
    """Initial Scraping Request producer

    Generates ScrapeRequest instances foreach HTTP request in the 'requests' list.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param requests: list[dict[str, any]]   List of requests to generate
    :return: None
    """
    while len(requests) > 0:
        r = requests.pop()
        url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
        logger.debug('Producing %s request: %s', r['method'], r['url'])
        r['metadata']['url'] = url
        await queue.put(
            ScrapeRequest(
                metadata=r['metadata'],
                request=client.request(method=r['method'], url=url),
                consumer=r['consumer']
            )
        )


async def handle_redirect(
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


async def handle_success(
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


async def handle_scrape_request_consumer_exception(
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
                await handle_redirect(scrape_request, queue, client)
            elif scrape_request.response.is_success:    # Process successful requests
                await handle_success(scrape_request, queue, response_queue, client)
            else:
                raise Exception(f'Unknown status code {scrape_request.response.status}')

            # Remove processed item from queue
            queue.task_done()
            logger.debug('Task removed from queue.')

        # Handle Exceptions if any
        except Exception as e:
            await handle_scrape_request_consumer_exception(e, scrape_request, queue, client)

        finally:
            if scrape_request is not None:
                logger.info(f'Finished processing request {scrape_request.url}. '
                            f'Request queue: {queue.qsize()}; Response queue: {response_queue.qsize()}')
            logger.debug(f'Request Consumer Released, sleeping...')

            # Sleep consumer for configured amount of time
            await asyncio.sleep(CONSUMER_SLEEP_TIME)
            logger.debug('Resuming Request Consumer.')


async def scrape_response_consumer(response_queue: asyncio.Queue) -> None:
    """Scraping Response consumer

    :param response_queue: asyncio.Queue    Scrape Response queue
    :return: None
    """
    logger.debug(f'Starting Response Consumer')
    while True:
        __queue_item = await response_queue.get()
        logger.debug('Got response from queue: %s', __queue_item)

        if __queue_item.data is not None:
            with jsonlines.open('./out/data-crawler/data.jsonl', 'a') as _:
                _.write(__queue_item.jsonl())

        response_queue.task_done()
        logger.debug('Task removed from queue.')
        logger.info('Wrote response to file.')

        logger.debug(f'Response Consumer Idle. Sleeping...')
        await asyncio.sleep(CONSUMER_SLEEP_TIME)
        logger.debug('Resuming Response Consumer.')


async def scrape_request_handler(
        requests: list[dict[str, any]],
        client: AsyncClient = AsyncClient(**HTTP_CLIENT_CONFIG),     # Async HTTP Client
        queue: asyncio.Queue = None,     # Queue for ScrapeRequest objects
        response_queue: asyncio.Queue = None,  # Queue for ScrapeResponse objects
) -> None:
    """Asynchronous ScrapeRequest Handler

    :param requests: list[dict[str, any]]   List of requests to generate
    :param client: AsyncClient      HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue     Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    :return: None
    """
    logger.debug('Start scrape request handler.')

    # Init queues if not provided in kwargs
    if queue is None:
        queue = asyncio.Queue()
    if response_queue is None:
        response_queue = asyncio.Queue()

    Path('./out/data-crawler').mkdir(parents=True, exist_ok=True)

    # Producer and Consumer generation
    producers = [  # Build and publish in queue the ScrapeRequest for each stock through producers
        asyncio.create_task(scrape_request_producer(client, queue, requests))
        for _ in range(3)
    ]
    logger.debug('Generated producers for ScrapeRequest object generation.')

    request_consumers = [  # Generate consumers to process the ScrapeRequest objects
        asyncio.create_task(scrape_request_consumer(client, queue, response_queue))
        for _ in range(NO_REQUEST_CONSUMERS)
    ]
    logger.debug('Generated consumers for ScrapeRequest object processing.')

    response_consumers = [  # Generate consumers to process the ScrapeRequest objects
        asyncio.create_task(scrape_response_consumer(response_queue))
        for _ in range(NO_RESPONSE_CONSUMERS)
    ]
    logger.debug('Generated consumers for ScrapeRequest object processing.')

    # Wait for producers and consumers to finish their processes
    await asyncio.gather(*producers)  # wait for producers to finish

    await queue.join()  # Wait for consumers to finish and stop them
    [_.cancel() for _ in request_consumers]

    await response_queue.join()  # Wait for consumers to finish and stop them
    [_.cancel() for _ in response_consumers]

    logger.debug('Finished scrape request handler.')
    return None
