import asyncio

from typing import Callable, Coroutine, Awaitable
from inspect import iscoroutinefunction

import httpx
from httpx import AsyncClient


class Request:
    __metadata: dict
    __request: httpx.Request or Coroutine[Callable[..., Awaitable[None]]]
    __response: httpx.Response
    __consumer: Callable

    def __init__(
            self,
            metadata: dict,
            request: httpx.Request or Coroutine[Callable[..., Awaitable[None]]],
            consumer: Callable
    ) -> None:
        self.__metadata = metadata.copy()
        self.__request = request
        self.__consumer = consumer

    @property
    def metadata(self) -> dict:
        return self.__metadata

    @property
    async def request(self) -> httpx.Request or Coroutine[Callable[..., Awaitable[None]]]:
        self.__response = await self.__request
        return self.__response

    @property
    def response(self):
        return self.__response

    @property
    def consumer(self) -> Callable:
        return self.__consumer


# class Response:
#     __metadata: dict
#     __response: httpx.Response
#
#     def __init__(self, metadata: dict, response: httpx.Response) -> None:
#         self.__metadata = metadata.copy()
#         self.__response = response
#
#     @property
#     def metadata(self) -> dict:
#         return self.__metadata
#
#     @property
#     def response(self) -> httpx.Response:
#         return self.__response


async def request_producer(client: AsyncClient, queue: asyncio.Queue, requests: list[dict[str, any]]):
    while len(requests) > 0:
        r = requests.pop()
        url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
        await queue.put(
            Request(
                metadata=r['metadata'],
                request=client.request(method=r['method'], url=url),
                consumer=r['consumer']
            )
        )


async def request_consumer(
        client: AsyncClient,
        queue: asyncio.Queue,
        response_queue: asyncio.Queue
):
    while True:
        __queue_item = await queue.get()

        # Verify queue item is a compatible Request, remove if not
        if type(__queue_item) is not Request:
            # must log 'Queue items must be of type Request'
            queue.task_done()
            continue

        await __queue_item.request

        # Process redirected responses
        if __queue_item.response.is_redirect:
            url = __queue_item.response.headers['Location']
            if 'url_append' in __queue_item.metadata.keys():
                url += __queue_item.metadata['url_append']
            __queue_item.metadata.update({'redirected': {'from': __queue_item.response.request.url, 'to': url}})
            await queue.put(
                Request(
                    metadata=__queue_item.metadata,
                    request=client.request(method=__queue_item.response.request.method, url=url),
                    consumer=__queue_item.consumer
                )
            )

        # Process successful requests
        elif __queue_item.response.is_success:
            if iscoroutinefunction(__queue_item.consumer):
                response = await __queue_item.consumer(__queue_item.response.text)
            else:
                response = __queue_item.consumer(__queue_item.response.text)
            await response_queue.put(response)

        # Remove processed item from queue
        queue.task_done()
