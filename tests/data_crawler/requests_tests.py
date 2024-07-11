import unittest
import asyncio
import logging
import httpx
import pypdf

from unittest import mock
from httpx import AsyncClient
from io import BytesIO

from src.data_crawler.constants import ASYNC_AWAIT_TIMEOUT, LOGGING_CONFIG
from src.data_crawler.scrape_requests.handlers.scrape_request_handler import scrape_request_handler
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.scrape_requests.handlers.producers import ScrapeRequestsProducer
from src.data_crawler.scrape_requests.handlers.consumers import ScrapeRequestConsumer
from src.data_crawler.parsers.ar_parse import parse_firms_detail_page

# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('Requests Tests')


class ProducerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')
        self.queue = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)
        self.sample_request = {
            'metadata': {
                'url_append': '/financial-statements-and-reports'
            },
            'method': 'GET',
            'url': 'ttps://www.hl.co.uk/shares/shares-search-results/B6VTTK0',
            'consumer': lambda x: ScrapeResponse({}, '', [])
        }
        self.requests = [self.sample_request]

    async def test_request_producer(self):
        async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
            producers = [
                asyncio.create_task(ScrapeRequestsProducer(self.client, self.queue, self.requests, _)())
                for _ in range(3)
            ]
            await asyncio.gather(*producers)

            self.assertEqual(1, self.queue.qsize())

            item = await self.queue.get()

            self.assertEqual(ScrapeRequest, type(item))
            self.assertEqual(self.sample_request['metadata'], item.metadata)

            await item.send()

            self.client.request.assert_awaited_with(
                method=self.sample_request['method'],
                url=self.sample_request['url'] + self.sample_request['metadata']['url_append']
            )
            self.queue.task_done()

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20} ')


class ConsumerTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')
        self.queue = asyncio.Queue()
        self.responses = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)

        self.request_params = {
            'method': 'GET',
            'url': 'https://www.hl.co.uk/shares/shares-search-results/B6VTTK0/financial-statements-and-reports'
        }

        self.client.request = mock.AsyncMock(return_value=httpx.Response(
            status_code=200, content='sample content', request=httpx.Request(**self.request_params)
        ))

        self.sample_request = ScrapeRequest(
            metadata={
                'url_append': '/financial-statements-and-reports'
            },
            request=self.client.request(**self.request_params),
            consumer=lambda x, client: tuple([{}, '', []])
        )

    async def test_request_consumer(self):
        async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
            await self.queue.put(self.sample_request)

            # Error esta en obtener el delay pues no hace peticiones http; hay que hace mock de esos metodos
            self.consumers = [
                asyncio.create_task(ScrapeRequestConsumer(self.client, self.queue, self.responses, _)())
                for _ in range(10)
            ]

            await self.queue.join()

            self.client.request.assert_awaited_once()
            self.client.request.assert_awaited_with(**self.request_params)
            self.assertFalse(self.responses.empty())
            self.assertEqual(1, self.responses.qsize())

            item = await self.responses.get()
            self.responses.task_done()

            self.assertTrue(type(item) is ScrapeResponse)
            self.assertEqual({'method': 'GET'}, item.metadata)
            self.assertEqual('', item.data)
            self.assertEqual([], item.further_requests)

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20} ')
        [c.cancel() for c in self.consumers]


class ConsumerRedirectTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')
        self.queue = asyncio.Queue()
        self.responses = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)
        self.client.request = mock.AsyncMock()
        self.request_params = {
            'method': 'GET',
            'url': 'https://www.hl.co.uk/shares/shares-search-results/B6VTTK0/financial-statements-and-reports'
        }
        request = self.client.request(**self.request_params)
        self.client.request.side_effect = [
            httpx.Response(status_code=301, headers={'Location': '/foo'}, request=httpx.Request(**self.request_params)),
            httpx.Response(status_code=200, content='sample content', request=httpx.Request(**self.request_params)),
        ]
        self.sample_request = ScrapeRequest(
            metadata={
                'url_append': '/financial-statements-and-reports'
            },
            request=request,
            consumer=lambda x, client: tuple([{}, '', []])
        )

    async def test_request_consumer_with_redirect(self):
        async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
            await self.queue.put(self.sample_request)

            self.consumers = [
                asyncio.create_task(ScrapeRequestConsumer(self.client, self.queue, self.responses, _)())
                for _ in range(10)
            ]

            await self.queue.join()
            [c.cancel() for c in self.consumers]

            self.assertEqual(2, self.client.request.await_count)
            self.client.request.assert_awaited_with(
                method='GET',
                url='https://www.hl.co.uk/foo/financial-statements-and-reports'
            )
            self.assertFalse(self.responses.empty())
            self.assertEqual(1, self.responses.qsize())

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20} ')
        [c.cancel() for c in self.consumers]


class ConsumerRequestTypeExceptionTest(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')
        self.queue = asyncio.Queue()
        self.responses = asyncio.Queue()
        self.client = mock.AsyncMock(AsyncClient)
        self.sample_request = {}

    async def test_request_consumer(self):
        async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
            await self.queue.put(self.sample_request)

            self.consumers = [
                asyncio.create_task(ScrapeRequestConsumer(self.client, self.queue, self.responses, _)())
                for _ in range(10)
            ]

            await self.queue.join()

            self.client.request.assert_not_awaited()
            self.assertTrue(self.responses.empty())

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20} ')
        [c.cancel() for c in self.consumers]


class ScrapeRequestHandlerTestCase(unittest.IsolatedAsyncioTestCase):
    """Test Scrape Request Handler"""

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load html response mocks from files
        with open('./tests/mocks/data_crawler/ar-firm-detail-page-abrdn.mock.html', 'r') as _:
            self.firms_detail_page_response_mock = _.read()

        # Set mock request
        self.request_mock = mock.MagicMock(httpx.Request, method='GET', url='http://test.url')

        # Set pdf response contents
        writer = pypdf.PdfWriter()
        writer.add_blank_page(100, 100)
        byte_stream = BytesIO()
        writer.write_stream(byte_stream)
        byte_stream.seek(0)
        self.pdf_response_mock = byte_stream.read()

    @mock.patch('httpx.AsyncClient.request', new_callable=mock.AsyncMock)
    async def test_scrape_ar_firm_detail_page(self, async_client_mock: mock.AsyncMock) -> None:
        """Test the scraping of the stocks' financial statements page"""
        # Set Up Mocks
        async_client_mock.side_effect = [
            httpx.Response(200, content=self.firms_detail_page_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock)
        ]

        # Call function
        async with asyncio.timeout(ASYNC_AWAIT_TIMEOUT):
            await scrape_request_handler([
                {
                    'metadata': {},
                    'method': 'GET',
                    'url': '',
                    'consumer': parse_firms_detail_page
                }
            ])

        # Assert
        self.assertNoLogs(logging.getLogger('asyncio'), logging.ERROR)
        self.assertEqual(11, async_client_mock.await_count)

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


class ScrapeRequestRestartTestCase(unittest.IsolatedAsyncioTestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')
        self.client_ex = mock.AsyncMock(AsyncClient)
        self.client_ex.request.side_effect = Exception()

        self.client = mock.AsyncMock(AsyncClient)
        self.client.request.side_effect = [httpx.Response(200, content='sample content')]

    async def test_request_restart(self):
        request = ScrapeRequest(
            metadata={
                'url': '',
                'method': 'GET'
            },
            request=self.client_ex.request(method='GET', url='http://test.url'),
            consumer=lambda x, y: True
        )
        with self.assertRaises(Exception):
            await request.send()

        self.client_ex.request.assert_awaited_once()

        self.assertTrue(request.get_postmortem_log() is not None)

        self.assertTrue(type(request.reset(client=self.client)), ScrapeRequest)
        await request.send()
        self.client.request.assert_awaited_once()

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
