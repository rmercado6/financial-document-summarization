import logging
import asyncio

from logging.handlers import QueueHandler
from logging.handlers import QueueListener
from logging import StreamHandler
from queue import Queue

from src.data_crawler.constants import LOGGING_CONFIG


LOGGER_TASK = None  # reference to the logger task


async def init_logger() -> None:
    """Helper coroutine to set up and manage the Logger"""
    q = Queue()   # create the shared queue

    # Format output
    logging.basicConfig(
        **LOGGING_CONFIG['prod'],
        handlers=[QueueHandler(q)]
    )

    # create a listener for messages on the queue
    listener = QueueListener(q, StreamHandler())
    try:
        listener.start()    # start the listener
        logging.debug('Logger has started')     # report the logger is ready
        while True:     # wait forever
            await asyncio.sleep(60)
    finally:
        logging.debug(f'Logger is shutting down')   # report the logger is done
        listener.stop()     # ensure the listener is closed


async def safely_start_logger() -> None:
    """Coroutine to safely start the Logger"""
    global LOGGER_TASK
    LOGGER_TASK = asyncio.create_task(init_logger())    # initialize the logger
    await asyncio.sleep(0)  # allow the logger to start
