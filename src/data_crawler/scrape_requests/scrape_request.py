import httpx

from typing import Coroutine, Callable, Awaitable, Any


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
        if "url" not in self.__metadata.keys():
            self.__metadata["url"] = ''

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

    @property
    def url(self) -> str:
        try:
            return str(self.__response.request.url)
        except AttributeError or Exception:
            return self.metadata["url"]

    async def send(self) -> httpx.Response:
        """To be used to await for the http request."""
        self.__response = await self.__request
        return self.__response

    def reset(self, client: httpx.AsyncClient) -> int:
        try:
            self.__request = client.request(method=self.request.method, url=self.request.url)
        except AttributeError or Exception:
            self.__request = client.request(method=self.metadata['method'], url=self.metadata['url'])
        self.__reset_count += 1
        return self.__reset_count

    def get_postmortem_log(self) -> dict:
        try:
            return {
                'response': self.response.status_code,
                'metadata': self.metadata,
                'resets': self.__reset_count
            }
        except AttributeError or Exception:
            return {'response': None, 'metadata': self.metadata, 'resets': self.__reset_count}
