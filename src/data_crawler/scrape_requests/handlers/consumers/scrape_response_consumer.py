import asyncio

import jsonlines

from asyncio import Queue
from httpx import AsyncClient

from src.data_crawler.scrape_requests import ScrapeResponse
from src.data_crawler.scrape_requests.handlers import AsyncTask
from src.data_crawler.constants import CONSUMER_SLEEP_TIME
from . import handle_consumer_exception


writer_lock = asyncio.Lock()


class ScrapeResponseConsumer(AsyncTask):

    def __init__(self, client: AsyncClient, task_queue: Queue, response_queue: Queue, task_id: any = None):
        super().__init__(client, task_queue, response_queue, task_id)

    @AsyncTask.id.getter
    def id(self) -> str:
        return f'SRPC-{super().id}'

    async def __call__(self) -> None:
        """Scraping Response consumer

        :return: None
        """
        self.debug(f'Starting Response Consumer')
        scrape_response: ScrapeResponse or None = None
        while True:
            try:
                self.info(f'Task Queue: {self.task_queue.qsize()} | Response Queue: {self.response_queue.qsize()}')
                scrape_response = await self.response_queue.get()
                self.debug(f'Got response from queue: {scrape_response}')

                # Verify task queue item is a compatible Request, remove if not
                if type(scrape_response) is not ScrapeResponse:
                    self.warning(f'Bad request from task queue. '
                                 f'{type(scrape_response)} object is not a ScrapeResponse object.')
                    self.task_queue.task_done()
                    continue

                tasks = await asyncio.gather(scrape_response.jsonl())
                jsonline = tasks[0]
                if jsonline["doc"] is not None:
                    async with writer_lock:
                        with jsonlines.open('./out/data-crawler/data.jsonl', 'a') as _:
                            _.write(jsonline)

                self.response_queue.task_done()
                self.debug('Task removed from queue.')

            except Exception as e:
                self.error('Error while processing scrape response.')
                await handle_consumer_exception(e, scrape_response, self)

            finally:
                await asyncio.sleep(CONSUMER_SLEEP_TIME)
