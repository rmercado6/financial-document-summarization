import unittest
import logging

import httpx

from unittest.mock import patch, MagicMock

from src.data_crawler.constants import LOGGING_CONFIG
from src.data_crawler.scraping.ar_scrape import scrape_ar_stocks_table

# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('AR Scrape Tests')


class ARScrapeStocksTableTest(unittest.TestCase):
    """Test case for testing the scraping of the stocks table"""

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load html response mocks from files
        with open('./tests/mocks/data_crawler/ar-stocks-table.mock.html', 'r') as _:
            self.stocks_table_response_mock = _.read()

    @patch('httpx.Client.get', new_callable=MagicMock)
    def test_scrape_ar_stocks_table(self, async_client_mock: MagicMock) -> None:
        """Test the scraping of the stocks table"""
        # Set up Mocks
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=self.stocks_table_response_mock
        )

        # Call method
        r = scrape_ar_stocks_table('')

        # Assert
        async_client_mock.assert_called_once()
        self.assertEqual(list, type(r))
        self.assertEqual(1379, len(r))
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
