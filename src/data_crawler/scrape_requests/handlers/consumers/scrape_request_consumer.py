import contextvars
import logging
import asyncio
import time

from httpx import AsyncClient, URL
from urllib.robotparser import RobotFileParser

from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.scrape_requests.handlers import redirect_handler, success_handler, AsyncTask
from src.data_crawler.scrape_requests.handlers.consumers import consumer_exception_handler
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
    :param task_queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    """

    def __init__(
            self,
            client: AsyncClient,
            task_queue: asyncio.Queue,
            response_queue: asyncio.Queue,
            task_id: any = None
    ) -> None:
        super().__init__(client, task_queue, response_queue, task_id)

    @AsyncTask.id.getter
    def id(self) -> str:
        return f'SRQC-{super().id}'

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
                self.info(f'START | '
                          f'Task Queue: {self.task_queue.qsize()} | Response Queue: {self.response_queue.qsize()}')
                # Get scrape request from queue
                scrape_request = await self.task_queue.get()
                self.debug(f'Got request from task queue[{self.task_queue.qsize()}]: {scrape_request}')

                # Verify task queue item is a compatible Request, remove if not
                if type(scrape_request) is not ScrapeRequest:
                    self.warning(f'Bad request from task queue. '
                                 f'{type(scrape_request)} object is not a ScrapeRequest object.')
                    self.task_queue.task_done()
                    continue

                # Verify time between requests to respect politeness while crawling
                await self.delay_request(URL(scrape_request.url))

                # Execute http request
                await scrape_request.send()

                response = ScrapeResponse(scrape_request)
                # Process response
                self.info(f'Processing Scrape Response {response.url}')
                if response.is_redirect:     # Process redirected responses
                    await redirect_handler(response, self.task_queue, self.client)
                elif response.is_success:    # Process successful requests
                    await success_handler(response, self.task_queue, self.response_queue, self.client)
                else:
                    raise Exception(f'Unknown status code {response.status}')

                # Remove processed item from queue
                self.task_queue.task_done()
                self.debug('Task removed from queue.')

            # Handle Exceptions if any
            except Exception as e:
                self.error('Error while processing scrape request.')
                await consumer_exception_handler(e, scrape_request, self)

            finally:
                if scrape_request is not None:
                    self.info(f'END')
                self.debug(f'Request Consumer Released, sleeping...')

                # Sleep consumer for configured amount of time
                await asyncio.sleep(CONSUMER_SLEEP_TIME)
                self.debug('Resuming Request Consumer.')
