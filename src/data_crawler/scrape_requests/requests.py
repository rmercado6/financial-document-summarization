from typing import Coroutine, Callable, Awaitable, Any

import httpx


class ScrapeRequest:
    """ScrapeRequests class
    Abstracts the information of each of the scraping requests.
    """
    __metadata: dict
    __request: httpx.Request or Coroutine[Callable[..., Awaitable[None]]]
    __consumer: Callable
    __response: httpx.Response = None
    __reset_count = 0

    def __init__(
            self,
            metadata: dict,
            request: Coroutine[httpx.request, Any, httpx.Response],
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
    def request(self) -> httpx.Request:
        """request: httpx.Request"""
        return self.__response.request if self.__response else None

    @property
    def response(self) -> httpx.Response:
        """response: httpx.Response"""
        return self.__response

    @property
    def consumer(self) -> Callable[..., Any]:
        """consumer: Callable"""
        return self.__consumer

    async def send(self) -> httpx.Response:
        """To be used to await for the http request."""
        self.__response = await self.__request
        return self.__response

    def reset(self, client: httpx.AsyncClient) -> int:
        self.__request = client.request(
            method=self.request.method if self.request else self.metadata['method'],
            url=self.request.url if self.request else self.metadata['url'],
        )
        self.__reset_count += 1
        return self.__reset_count

    def get_postmortem_log(self) -> dict:
        return {
            'response': self.response.status_code if self.response else None,
            'metadata': self.metadata if self.metadata else None
        }


class ScrapeResponse:
    """ConsumerResponse class
    Wrapper for the scraping responses.
    """
    __metadata: dict
    __data: str or bytes
    __further_requests: list[ScrapeRequest] or None

    def __init__(self, metadata: dict, data: str or bytes, further_requests: list[ScrapeRequest] = None) -> None:
        self.__metadata = metadata.copy()
        if 'method' not in self.__metadata:
            self.__metadata['method'] = 'GET'
        self.__data = data
        self.__further_requests = further_requests

    @property
    def metadata(self) -> dict:
        """metadata: dict"""
        return self.__metadata

    @property
    def data(self) -> str or bytes:
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

    def jsonl(self) -> dict:
        return {
            'title': self.metadata['share']['title'],
            'ticker': self.metadata['share']['ticker'],
            'year': self.metadata['year'] if 'year' in self.metadata.keys() else None,
            'document_type': self.metadata['data_type'],
            'doc': self.data if type(self.data) is str else self.data.decode('utf-8'),
        }
