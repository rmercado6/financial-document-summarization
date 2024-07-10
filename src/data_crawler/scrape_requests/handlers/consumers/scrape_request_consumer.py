import logging
import asyncio
import uuid

from httpx import AsyncClient

from src.data_crawler.scrape_requests import ScrapeRequest
from src.data_crawler.scrape_requests.handlers import redirect_handler, success_handler
from src.data_crawler.scrape_requests.handlers.consumers import consumer_exception_handler
from src.data_crawler.constants import LOGGER_NAME, CONSUMER_SLEEP_TIME


logger = logging.getLogger(LOGGER_NAME)


class ScrapeRequestConsumer:
    """Scraping Request consumer

    Processes and handles requests through the scraping process.

    :param client: AsyncClient  HTTP Client for managing HTTP requests
    :param queue: asyncio.Queue Scrape Request queue
    :param response_queue: asyncio.Queue    Scrape Response queue
    """

    __id: str
    __client: AsyncClient
    __queue: asyncio.Queue
    __response_queue: asyncio.Queue

    def __init__(
            self,
            client: AsyncClient,
            queue: asyncio.Queue,
            response_queue: asyncio.Queue,
            sr_id: any = None
    ) -> None:
        self.__id = str(uuid.uuid4()) if sr_id is None else str(sr_id)
        self.__client = client
        self.__queue = queue
        self.__response_queue = response_queue

    @property
    def id(self) -> str:
        return f'SR-{self.__id}'

    @property
    def client(self):
        return self.__client

    @property
    def queue(self):
        return self.__queue

    @property
    def response_queue(self):
        return self.__response_queue

    def info(self, msg: str) -> None:
        logger.info(f'{self.id} | {msg}')

    def debug(self, msg: str) -> None:
        logger.debug(f'{self.id} | {msg}')

    def error(self, msg: str) -> None:
        logger.error(f'{self.id} | {msg}')

    def warning(self, msg: str) -> None:
        logger.warning(f'{self.id} | {msg}')

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
                    self.warning(f'Bad request from queue. {type(scrape_request)} object is not a ScrapeRequest object.')
                    self.queue.task_done()
                    continue

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


