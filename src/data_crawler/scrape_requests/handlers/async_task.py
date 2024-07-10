import logging
import uuid

from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class AsyncTask:

    __id: str

    def __init__(self, srpc_id: any = None):
        self.__id = str(uuid.uuid4()) if srpc_id is None else str(srpc_id)

    @property
    def id(self):
        return self.__id

    def info(self, msg: str) -> None:
        logger.info(f'{self.id} | {msg}')

    def debug(self, msg: str) -> None:
        logger.debug(f'{self.id} | {msg}')

    def error(self, msg: str) -> None:
        logger.error(f'{self.id} | {msg}')

    def warning(self, msg: str) -> None:
        logger.warning(f'{self.id} | {msg}')