from typing import Coroutine, Callable, Awaitable, Any

import httpx


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
