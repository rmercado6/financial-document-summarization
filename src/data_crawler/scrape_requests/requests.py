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

    def restart(self, client: httpx.AsyncClient):
        self.__request = client.request(
            method=self.response.request.method,
            url=self.response.request.url
        )
        return self

    def get_postmortem_log(self) -> dict:
        return {
            'url': self.response.request.url,
            'response': self.response.status_code,
            'metadata': self.metadata
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
