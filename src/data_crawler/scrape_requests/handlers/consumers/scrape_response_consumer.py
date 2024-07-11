import asyncio
import jsonlines

from asyncio import Queue
from httpx import AsyncClient

from src.data_crawler.scrape_requests import ScrapeResponse
from src.data_crawler.scrape_requests.handlers import AsyncTask, redirect_handler, success_handler
from src.data_crawler.constants import CONSUMER_SLEEP_TIME


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
        while True:
            scrape_response: ScrapeResponse = await self.response_queue.get()
            self.debug(f'Got response from queue: {scrape_response}')

            # Verify task queue item is a compatible Request, remove if not
            if type(scrape_response) is not ScrapeResponse:
                self.warning(f'Bad request from task queue. '
                             f'{type(scrape_response)} object is not a ScrapeResponse object.')
                self.task_queue.task_done()
                continue

            if scrape_response.data is not None:
                with jsonlines.open('./out/data-crawler/data.jsonl', 'a') as _:
                    _.write(scrape_response.jsonl())

            self.response_queue.task_done()
            self.debug('Task removed from queue.')
            # self.info('Wrote response to file.')

            await asyncio.sleep(CONSUMER_SLEEP_TIME)
