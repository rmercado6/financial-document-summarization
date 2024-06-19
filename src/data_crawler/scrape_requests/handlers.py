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
        __queue_item: ScrapeRequest or None = None
        try:
            logger.debug('Request Consumer looking on queue for response to handle. qsize: %s',
                         queue.qsize())
            __queue_item = await queue.get()
            logger.debug('Got request from queue[%s]: %s', queue.qsize(), __queue_item)

            # Verify queue item is a compatible Request, remove if not
            if type(__queue_item) is not ScrapeRequest:
                logger.warning(f'Bad request from queue. {type(__queue_item)} object is not a ScrapeRequest object.')
                queue.task_done()
                continue

            await __queue_item.send()

            logger.info('Processing Scrape Request %s', __queue_item.url)

            # Process redirected responses
            if __queue_item.response.is_redirect:
                logger.info(f'Redirecting request {__queue_item.url} to {__queue_item.response.headers["Location"]}')

                # Build new URL
                url = httpx.URL(__queue_item.response.headers['Location'])
                if not url.host:
                    url = httpx.URL(
                        __queue_item.response.headers['Location'],
                        host=__queue_item.response.request.url.host,
                        scheme=__queue_item.response.request.url.scheme
                    )
                url = str(url)
                if 'url_append' in __queue_item.metadata.keys():
                    url += __queue_item.metadata['url_append']

                # Update metadata with redirect tracking information
                __queue_item.metadata.update({
                    'redirected_from': __queue_item.url,
                    'url': url
                })

                # Add new request to queue
                await queue.put(
                    ScrapeRequest(
                        metadata=__queue_item.metadata,
                        request=client.request(method=__queue_item.request.method, url=url),
                        consumer=__queue_item.consumer
                    )
                )

            # Process successful requests
            elif __queue_item.response.is_success:
                logger.debug(f'Successful request from queue: {__queue_item.url}. '
                             f'Sending request to consumer function {__queue_item.consumer.__name__}.')

                response: ScrapeResponse = __queue_item.consumer(__queue_item, client=client)

                logger.debug(f'Got response from consumer function.')
                await response_queue.put(response)
                if response.further_requests:
                    logger.debug(f'Adding {len(response.further_requests)} requests to request queue with '
                                 f'actual qsize {queue.qsize()}.')
                    [await queue.put(request) for request in response.further_requests]
                    logger.debug(f'Added {len(response.further_requests)} requests to request queue with '
                                 f'updated qsize {queue.qsize()}.')

            else:
                raise Exception(f'Unknown status code {__queue_item.response.status}')

            queue.task_done()  # Remove processed item from queue
            logger.debug('Task removed from queue.')

        # Handle Exceptions if any
        except Exception as e:
            if __queue_item is not None:
                logger.warning('Error consuming ScrapeRequest %s', __queue_item.url)
                # Log error to file
                with jsonlines.open('./out/data-crawler/error.jsonl', 'a') as _:
                    _.write(__queue_item.get_postmortem_log())
                if __queue_item.reset(client) < MAX_RETRIES:
                    await queue.put(__queue_item)
            else:
                logger.warning('Error attempting to get ScrapeRequest from queue.')
                raise e

            logger.exception(e)
            queue.task_done()

        finally:
            if __queue_item is not None:
                logger.info(f'Finished processing request {__queue_item.url}. '
                            f'Request queue: {queue.qsize()}; Response queue: {response_queue.qsize()}')
            logger.debug(f'Request Consumer Released, sleeping...')
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
