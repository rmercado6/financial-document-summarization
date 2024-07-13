import logging
import uuid
from asyncio import Queue

from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class AsyncTask:

    __id: str
    __client: AsyncClient
    __task_queue: Queue
    __response_queue: Queue

    def __init__(self, client: AsyncClient, task_queue: Queue, response_queue: Queue or None, task_id: any = None):
        self.__id = str(uuid.uuid4()) if task_id is None else str(task_id)
        self.__client = client
        self.__task_queue = task_queue
        self.__response_queue = response_queue

    @property
    def id(self):
        return self.__id

    @property
    def client(self):
        return self.__client

    @property
    def task_queue(self):
        return self.__task_queue

    @property
    def response_queue(self):
        return self.__response_queue

    def info(self, msg: str) -> None:
        logger.info(f'{self.id} | {msg}')

    def debug(self, msg: str) -> None:
        logger.debug(f'{self.id} | {msg}')

    def warning(self, msg: str) -> None:
        logger.warning(f'{self.id} | {msg}')

    def error(self, msg: str) -> None:
        logger.error(f'{self.id} | {msg}')

    def exception(self, exception: Exception) -> None:
        logger.exception(f'{self.id} | {exception}')
