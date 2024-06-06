import unittest
import asyncio
from unittest import mock

from httpx import AsyncClient

from src.data_crawler.requests import request_consumer, request_producer


class ProducerTest(unittest.IsolatedAsyncioTestCase):
    async def test_request_producer(self):

        queue = asyncio.Queue()
        client = mock.AsyncMock(AsyncClient)

        sample_request = {
                'metadata': {
                    'url_append': '/financial-statements-and-reports'
                },
                'method': 'GET',
                'url': 'ttps://www.hl.co.uk/shares/shares-search-results/B6VTTK0'
            }
        requests = [sample_request]

        producers = [asyncio.create_task(request_producer(client, queue, requests)) for _ in range(3)]

        await asyncio.gather(*producers)

        self.assertEqual(1, queue.qsize())

        item = await queue.get()
        self.assertEqual(['metadata', 'request'], list(item.keys()))
        self.assertEqual(sample_request['metadata'], item['metadata'])
        response = await item['request']
        client.request.assert_awaited_with(
            method=sample_request['method'],
            url=sample_request['url'] + sample_request['metadata']['url_append']
        )
        queue.task_done()


class ConsumerTest(unittest.IsolatedAsyncioTestCase):
    async def test_request_consumer(self):
        self.assertEqual(True, False)  # add assertion here


if __name__ == '__main__':
    unittest.main()
