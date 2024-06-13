import unittest
import httpx
import pypdf
import logging

from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table
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
        self.assertEqual(list, type(r))
        self.assertEqual(110, len(r))
        item = r[0]
        self.assertTrue('metadata' in item.keys())
        self.assertTrue(type(item['metadata']) is dict)
        self.assertTrue('method' in item.keys())
        self.assertTrue(type(item['method']) is str)
        self.assertTrue('url' in item.keys())
        self.assertTrue(type(item['url']) is str)
        self.assertTrue('consumer' in item.keys())
        self.assertTrue(callable(type(item['consumer'])))

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
