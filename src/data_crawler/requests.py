import asyncio
import logging

import httpx

from typing import Callable, Coroutine, Awaitable, Any
from httpx import AsyncClient

from src.data_crawler.constants import ASYNC_AWAIT_TIMEOUT, LOGGER_NAME, HTTP_CLIENT_CONFIG


logger = logging.getLogger(LOGGER_NAME)


class ScrapeRequest:
    """ScrapeRequests class
    Abstracts the information of each of the scraping requests.
    """
    __metadata: dict
    __request: httpx.Request or Coroutine[Callable[..., Awaitable[None]]]
    __response: httpx.Response
    __consumer: Callable

    def __init__(
            self,
            metadata: dict,
            request: httpx.Request or Coroutine[Callable[..., Awaitable[None]]],
            consumer: Callable
    ) -> None:
        self.__metadata = metadata.copy()
        self.__request = request
        self.__consumer = consumer

    @property
    def metadata(self) -> dict:
        """metadata: dict"""
        return self.__metadata

    @property
    async def request(self) -> httpx.Response or Coroutine[Callable[..., Awaitable[None]]]:
        """request: httpx.Request
        To be used to await for the http request.
        """
        self.__response = await self.__request
        return self.__response

    @property
    def response(self):
        """response: httpx.Response"""
        return self.__response

    @property
    def consumer(self) -> Callable[..., Any]:
        """consumer: Callable"""
        return self.__consumer


class ScrapeResponse:
    """ConsumerResponse class
    Wrapper for the scraping responses.
    """
    __metadata: dict
    __data: any
    __further_requests: list[ScrapeRequest] or None

    def __init__(self, metadata: dict, data: any, further_requests: list[ScrapeRequest] = None) -> None:
        self.__metadata = metadata.copy()
        self.__data = data
        self.__further_requests = further_requests

    @property
    def metadata(self) -> dict:
        """metadata: dict"""
        return self.__metadata

    @property
    def data(self) -> any:
        """data: any
        The scraped data.
        """
        return self.__data

    @property
    def further_requests(self) -> list[ScrapeRequest]:
        """further_requests: list[ScrapeRequest]
        List of requests to further scrape, if any were generated during the scraping process.
        """
        return self.__further_requests


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
    """
    while len(requests) > 0:
        r = requests.pop()
        url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
        logger.debug('Producing %s request: %s', r['method'], r['url'])
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
    """
    async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
        logger.debug(f'Starting Consumer')
        while True:
            try:
                __queue_item = await queue.get()
                logger.debug('Got request from queue: %s', __queue_item)

                # Verify queue item is a compatible Request, remove if not
                if type(__queue_item) is not ScrapeRequest:
                    logger.warning(f'Bad request from queue. {type(__queue_item)} object is not a ScrapeRequest object.')
                    queue.task_done()
                    continue

                await __queue_item.request

                logger.info('Processing Scrape Request %s', __queue_item.response.request.url)

                # Process redirected responses
                if __queue_item.response.is_redirect:
                    logger.debug(f'Redirecting request {__queue_item.response.request.url} to {__queue_item.response.headers["Location"]}')

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
                    __queue_item.metadata.update({'redirected': {'from': __queue_item.response.request.url, 'to': url}})

                    # Add new request to queue
                    await queue.put(
                        ScrapeRequest(
                            metadata=__queue_item.metadata,
                            request=client.request(method=__queue_item.response.request.method, url=url),
                            consumer=__queue_item.consumer
                        )
                    )

                # Process successful requests
                elif __queue_item.response.is_success:
                    logger.debug(f'Successful request from queue: {__queue_item.response.request.url}. '
                                 f'Sending request to consumer function {__queue_item.consumer.__name__}.')
                    response: ScrapeResponse = __queue_item.consumer(__queue_item, client=client)
                    logger.debug(f'Got response from consumer function.')
                    await response_queue.put(response)
                    if response.further_requests:
                        [await queue.put(request) for request in response.further_requests]

                # Remove processed item from queue
                queue.task_done()

            # Handle Exceptions if any
            except Exception as e:
                logger.exception(e)

            finally:
                logger.debug(f'Consumer Idle')


async def scrape_request_handler(
        requests: list[dict[str, any]],
        client: AsyncClient = AsyncClient(**HTTP_CLIENT_CONFIG),     # Async HTTP Client
        queue: asyncio.Queue = None,     # Queue for ScrapeRequest objects
        response_queue: asyncio.Queue = None,  # Queue for ScrapeResponse objects
) -> None:
    """Asynchronous ScrapeRequest Handler"""
    logger.debug('Start scrape request handler.')

    # Init queues if not provided in kwargs
    if queue is None:
        queue = asyncio.Queue()
    if response_queue is None:
        response_queue = asyncio.Queue()

    # Producer and Consumer generation
    producers = [  # Build and publish in queue the ScrapeRequest for each stock through producers
        asyncio.create_task(scrape_request_producer(client, queue, requests))
        for _ in range(3)
    ]
    logger.debug('Generated producers for ScrapeRequest object generation.')

    consumers = [  # Generate consumers to process the ScrapeRequest objects
        asyncio.create_task(scrape_request_consumer(client, queue, response_queue))
        for _ in range(10)
    ]
    logger.debug('Generated consumers for ScrapeRequest object processing.')

    # Wait for producers and consumers to finish their processes
    await asyncio.gather(*producers)  # wait for producers to finish

    await queue.join()  # Wait for consumers to finish and stop them
    [c.cancel() for c in consumers]

    # TODO: Process responses (insert into non relational DB (Mongo) or write in jsonl file.
    logger.debug('Finished scrape request handler.')
    return None
