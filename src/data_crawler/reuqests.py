import asyncio

from typing import Callable
from inspect import iscoroutinefunction
from httpx import AsyncClient


async def request_producer(client: AsyncClient, queue: asyncio.Queue, requests: list[dict[str, any]]):
    while len(requests) > 0:
        r = requests.pop()
        url = r['url'] + r['metadata']['url_append'] if 'url_append' in r['metadata'].keys() else r['url']
        await queue.put({
            'metadata': r['metadata'],
            'request': client.request(method=r['method'], url=url),
        })


async def request_consumer(client: AsyncClient, queue: asyncio.Queue, consumer_function: Callable):
    while True:
        __queue_item = await queue.get()
        __response = await __queue_item['request']
        if __response.is_redirect:
            m = __queue_item['metadata']
            url = __response.headers['Location'] + m['url_append'] if 'url_append' in m.keys() else __response['url']
            m.update({
                'redirected': {
                    'from': __response.request.url,
                    'to': url
                }
            })
            await queue.put({
                'metadata': m,
                'request': client.request(method=__response.request.method, url=url)
            })
        elif __response.is_success:
            if iscoroutinefunction(consumer_function):
                await consumer_function(__response.text)
            else:
                consumer_function(__response.text)
        queue.task_done()
