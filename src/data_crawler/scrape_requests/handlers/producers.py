import logging
import asyncio

from httpx import AsyncClient

from src.data_crawler.scrape_requests.handlers import AsyncTask
from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class ScrapeRequestsProducer(AsyncTask):
    """Initial Scraping Request producer

    Generates ScrapeRequest instances foreach HTTP request in the 'requests' list.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param requests: list[dict[str, any]]   List of requests to generate
    :return: None
    """

    __request: list[dict[str, any]]

    def __init__(
            self,
            client: AsyncClient,
            queue: asyncio.Queue,
            requests: list[dict[str, any]],
            task_id: any = None
    ):
        super().__init__(client, queue, None, task_id)
        self.__requests = requests

    @AsyncTask.id.getter
    def id(self):
        return f'SRQP-{super().id}'

    @property
    def requests(self):
        return self.__requests

    async def __call__(self) -> None:
        while len(self.requests) > 0:
            r = self.requests.pop()
            url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
            self.debug(f"Producing {r['method']} request: {r['url']}")
            r['metadata']['url'] = url
            await self.task_queue.put(
                ScrapeRequest(
                    metadata=r['metadata'],
                    request=self.client.request(method=r['method'], url=url),
                    consumer=r['consumer']
                )
            )
