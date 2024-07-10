import asyncio

import jsonlines

from logging import getLogger

from src.data_crawler.constants import LOGGER_NAME, CONSUMER_SLEEP_TIME


logger = getLogger(LOGGER_NAME)


async def scrape_response_consumer(response_queue: asyncio.Queue) -> None:
    """Scraping Response consumer

    :param response_queue: asyncio.Queue    Scrape Response queue
    :return: None
    """
    logger.debug(f'Starting Response Consumer')
    while True:
        __queue_item = await response_queue.get()
        logger.debug('Got response from queue: %s', __queue_item)

        if __queue_item.data is not None:
            with jsonlines.open('./out/data-crawler/data.jsonl', 'a') as _:
                _.write(__queue_item.jsonl())

        response_queue.task_done()
        logger.debug('Task removed from queue.')
        logger.info('Wrote response to file.')

        logger.debug(f'Response Consumer Idle. Sleeping...')
        await asyncio.sleep(CONSUMER_SLEEP_TIME)
        logger.debug('Resuming Response Consumer.')
