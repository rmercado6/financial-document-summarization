import asyncio

import jsonlines

from src.data_crawler.scrape_requests.handlers.consumers import Consumer
from src.data_crawler.constants import CONSUMER_SLEEP_TIME


class ScrapeResponseConsumer(Consumer):

    __response_queue: asyncio.Queue

    def __init__(self, response_queue: asyncio.Queue, srpc_id: any = None):
        super().__init__(srpc_id)
        self.__response_queue = response_queue

    @Consumer.id.getter
    def id(self) -> str:
        return f'SRPC-{super().id}'

    @property
    def response_queue(self):
        return self.__response_queue

    async def __call__(self) -> None:
        """Scraping Response consumer

        :param response_queue: asyncio.Queue    Scrape Response queue
        :return: None
        """
        self.debug(f'Starting Response Consumer')
        while True:
            __queue_item = await self.response_queue.get()
            self.debug(f'Got response from queue: {__queue_item}')

            if __queue_item.data is not None:
                with jsonlines.open('./out/data-crawler/data.jsonl', 'a') as _:
                    _.write(__queue_item.jsonl())

            self.response_queue.task_done()
            self.debug('Task removed from queue.')
            self.info('Wrote response to file.')

            self.debug(f'Response Consumer Idle. Sleeping...')
            await asyncio.sleep(CONSUMER_SLEEP_TIME)
            self.debug('Resuming Response Consumer.')
