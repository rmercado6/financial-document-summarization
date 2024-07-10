import contextvars
import logging
import asyncio
import time

from httpx import AsyncClient, URL
from urllib.robotparser import RobotFileParser

from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.scrape_requests.handlers import redirect_handler, success_handler
from src.data_crawler.scrape_requests.handlers.consumers import consumer_exception_handler, AsyncTask
from src.data_crawler.constants import LOGGER_NAME, CONSUMER_SLEEP_TIME, ROBOTS_TXT_SUFFIX


logger = logging.getLogger(LOGGER_NAME)

request_times = contextvars.ContextVar('request_times')
request_times.set({})

robots_context = contextvars.ContextVar('robots_context')
robots_context.set({})


class ScrapeRequestConsumer(AsyncTask):
    """Scraping Request consumer

    Processes and handles requests through the scraping process.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    """

    __client: AsyncClient
    __queue: asyncio.Queue
    __response_queue: asyncio.Queue

    def __init__(
            self,
            client: AsyncClient,
            queue: asyncio.Queue,
            response_queue: asyncio.Queue,
            srpc_id: any = None
    ) -> None:
        super().__init__(srpc_id)
        self.__client = client
        self.__queue = queue
        self.__response_queue = response_queue

    @AsyncTask.id.getter
    def id(self) -> str:
        return f'SRQC-{super().id}'

    @property
    def client(self):
        return self.__client

    @property
    def queue(self):
        return self.__queue

    @property
    def response_queue(self):
        return self.__response_queue

    def get_request_delay(self, url: URL):
        self.debug(f'Getting request delay for {url}')
        _robots_context = robots_context.get()
        scheme = url.scheme + '://' if url.scheme else 'https://'
        if url.host not in _robots_context.keys():
            robots_parser = RobotFileParser(url=scheme + url.host + ROBOTS_TXT_SUFFIX)
            robots_parser.read()
            if robots_parser.crawl_delay("*"):
                _robots_context[url.host] = robots_parser.crawl_delay("*")
            else:
                _robots_context[url.host] = 0
            robots_context.set(_robots_context)
        self.debug(f'Request delay for {url} is of {_robots_context[url.host]}s')
        return _robots_context[url.host]

    async def delay_request(self, url: URL):
        self.debug(f'Starting delay request for {url}')
        _request_times = request_times.get()
        if url.host in _request_times.keys():
            while abs(time.time() - _request_times[url.host]) < self.get_request_delay(url):
                await asyncio.sleep(0)
        _request_times[url.host] = time.time()
        request_times.set(_request_times)
        self.debug(f'Finished delay request for {url}')

    async def __call__(self) -> None:
        self.debug(f'Starting Request Consumer {self.id}')
        while True:
            scrape_request: ScrapeRequest or None = None
            try:
                # Get scrape request from queue
                self.debug(f'Request Consumer looking on queue for response to handle. qsize: {self.queue.qsize()}')
                scrape_request = await self.queue.get()
                self.debug(f'Got request from queue[{self.queue.qsize()}]: {scrape_request}')

                # Verify queue item is a compatible Request, remove if not
                if type(scrape_request) is not ScrapeRequest:
                    self.warning(f'Bad request from queue. '
                                 f'{type(scrape_request)} object is not a ScrapeRequest object.')
                    self.queue.task_done()
                    continue

                # Verify time between requests to respect politeness while crawling
                await self.delay_request(URL(scrape_request.url))

                # Execute http request
                await scrape_request.send()

                # Process response
                self.info(f'Processing Scrape Request {scrape_request.url}')
                if scrape_request.response.is_redirect:     # Process redirected responses
                    await redirect_handler(scrape_request, self.queue, self.client)
                elif scrape_request.response.is_success:    # Process successful requests
                    await success_handler(scrape_request, self.queue, self.response_queue, self.client)
                else:
                    raise Exception(f'Unknown status code {scrape_request.response.status}')

                # Remove processed item from queue
                self.queue.task_done()
                self.debug('Task removed from queue.')

            # Handle Exceptions if any
            except Exception as e:
                await consumer_exception_handler(e, scrape_request, self.queue, self.client)

            finally:
                if scrape_request is not None:
                    self.info(f'Finished processing request {scrape_request.url}. '
                              f'Request queue: {self.queue.qsize()}; Response queue: {self.response_queue.qsize()}')
                self.debug(f'Request Consumer Released, sleeping...')

                # Sleep consumer for configured amount of time
                await asyncio.sleep(CONSUMER_SLEEP_TIME)
                self.debug('Resuming Request Consumer.')
