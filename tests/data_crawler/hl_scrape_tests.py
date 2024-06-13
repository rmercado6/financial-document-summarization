import unittest
import httpx
import pypdf
import logging

from io import BytesIO
from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.constants import LOGGING_CONFIG


# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('HL Scrape Tests')


class HlScrapeStocksTableTest(unittest.IsolatedAsyncioTestCase):
    """Asynchronous test case for testing the scraping of the stocks table"""

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load html response MOCKS from files
        with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as _:
            self.stocks_table_response_mock = _.read()

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_scrape_hl_index_stocks_table(self, async_client_mock: AsyncMock) -> None:
        """Test the scraping of the stocks table"""
        # Set up Mocks
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=self.stocks_table_response_mock
        )

        # Call method
        r = await scrape_hl_index_stocks_table('', 1)

        # Assert
        async_client_mock.assert_awaited_once_with("?page=1")
        self.assertEqual(dict, type(r))
        self.assertEqual(110, len(r.keys()))
        self.assertTrue('Abrdn plc' in r.keys())

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


class HlScrapeFinancialStatementsPageTest(unittest.IsolatedAsyncioTestCase):
    """Test the scraping of the financial statements page"""

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Set mock request
        self.request_mock = MagicMock(httpx.Request, method='GET', url='http://test.url')

        # Load html response MOCKS from files
        with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as _:
            self.financial_statements_page_response_mock = _.read()

        # Set pdf response contents
        writer = pypdf.PdfWriter()
        writer.add_blank_page(100, 100)
        byte_stream = BytesIO()
        writer.write_stream(byte_stream)
        byte_stream.seek(0)
        self.pdf_response_mock = byte_stream.read()

    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    async def test_scrape_hl_index_stock_pages(self, async_client_mock: AsyncMock) -> None:
        """Test the scraping of the stocks' financial statements page"""
        # Set Up Mocks
        async_client_mock.side_effect = [
            httpx.Response(200, content=self.financial_statements_page_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock)
        ]

        # Call function
        await scrape_hl_index_stock_pages({
            'Abrdn plc': '/shares/shares-search-results/BF8Q6K6',
        })

        # Assert
        self.assertEqual(3, async_client_mock.await_count)

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
