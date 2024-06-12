import asyncio
import httpx

from typing import Callable, Coroutine, Awaitable, Any
from httpx import AsyncClient

from src.data_crawler.constants import ASYNC_AWAIT_TIMEOUT


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
        while True:
            __queue_item = await queue.get()

            # Verify queue item is a compatible Request, remove if not
            if type(__queue_item) is not ScrapeRequest:
                # TODO: must log 'Queue items must be of type Request'
                queue.task_done()
                continue

            await __queue_item.request

            # Process redirected responses
            if __queue_item.response.is_redirect:
                url = httpx.URL(__queue_item.response.headers['location'])
                if not url.host:
                    url = httpx.URL(
                        __queue_item.response.headers['location'],
                        host=__queue_item.response.request.url.host,
                        scheme=__queue_item.response.request.url.scheme
                    )
                url = str(url)
                if 'url_append' in __queue_item.metadata.keys():
                    url += __queue_item.metadata['url_append']
                __queue_item.metadata.update({'redirected': {'from': __queue_item.response.request.url, 'to': url}})
                await queue.put(
                    ScrapeRequest(
                        metadata=__queue_item.metadata,
                        request=client.request(method=__queue_item.response.request.method, url=url),
                        consumer=__queue_item.consumer
                    )
                )

            # Process successful requests
            elif __queue_item.response.is_success:
                response: ScrapeResponse = __queue_item.consumer(__queue_item, client=client)
                await response_queue.put(response)
                if response.further_requests:
                    [await queue.put(request) for request in response.further_requests]

            # Remove processed item from queue
            queue.task_done()
