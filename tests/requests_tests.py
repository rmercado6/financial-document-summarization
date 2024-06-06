import unittest
import asyncio
import inspect
from unittest import mock

import httpx
from httpx import AsyncClient

from src.data_crawler.requests import request_consumer, request_producer


class ProducerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.queue = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)
        self.sample_request = {
            'metadata': {
                'url_append': '/financial-statements-and-reports'
            },
            'method': 'GET',
            'url': 'ttps://www.hl.co.uk/shares/shares-search-results/B6VTTK0'
        }
        self.requests = [self.sample_request]

    async def test_request_producer(self):
        producers = [asyncio.create_task(request_producer(self.client, self.queue, self.requests)) for _ in range(3)]
        await asyncio.gather(*producers)

        self.assertEqual(1, self.queue.qsize())

        item = await self.queue.get()

        self.assertEqual(['metadata', 'request'], list(item.keys()))
        self.assertEqual(self.sample_request['metadata'], item['metadata'])

        await item['request']

        self.client.request.assert_awaited_with(
            method=self.sample_request['method'],
            url=self.sample_request['url'] + self.sample_request['metadata']['url_append']
        )
        self.queue.task_done()


def parse_financial_statements_and_reports(s: str):
    return True


class ConsumerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        self.queue = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)
        self.client.request = mock.AsyncMock(return_value=httpx.Response(
            status_code=200, content='sample content'
        ))
        self.request_params = {
            'method': 'GET',
            'url': 'https://www.hl.co.uk/shares/shares-search-results/B6VTTK0/financial-statements-and-reports'
        }
        self.sample_request = {
            'metadata': {
                'url_append': '/financial-statements-and-reports'
            },
            'request': self.client.request(**self.request_params)
        }
        self.requests = [self.sample_request]

    async def test_request_consumer(self):
        await self.queue.put(self.sample_request)

        self.assertEqual(1, self.queue.qsize())

        self.consumers = [
            asyncio.create_task(request_consumer(self.client, self.queue, parse_financial_statements_and_reports))
            for _ in range(10)
        ]
        await self.queue.join()
        self.client.request.assert_awaited_once()
        self.client.request.assert_awaited_with(**self.request_params)

    def tearDown(self):
        [c.cancel() for c in self.consumers]


if __name__ == '__main__':
    unittest.main()
