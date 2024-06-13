import unittest
import logging
import inspect

from unittest.mock import MagicMock
from httpx import Client

from src.data_crawler.constants import LOGGING_CONFIG
from src.data_crawler.requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.ar_parse import parse_stocks_table, parse_firms_detail_page


# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('AR Parse Tests')


class ARParseStocksTableTest(unittest.TestCase):

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Set Up Mocks
        # Load mock response from file
        with open('./tests/mocks/data_crawler/ar-stocks-table.mock.html', 'r') as _:
            self.stocks_table_response_mock = _.read()

    def test_parse_stocks_table(self) -> None:
        """Test the parsing of the stocks table HTML"""

        # Call Method
        stocks: dict[str, str] = parse_stocks_table(self.stocks_table_response_mock)

        # Assert
        self.assertEqual(dict, type(stocks))
        self.assertEqual(1379, len(stocks.keys()))
        self.assertEqual('/Company/4imprint-group-plc', stocks['4imprint Group PLC'])

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {inspect.getframeinfo(inspect.currentframe()).function} case... {"-" * 20}')


class ARParseFirmsDetailPageTest(unittest.TestCase):
    """Test the different methods for parsing information from AnnualReports"""

    def setUp(self):
        logger.debug(f'{"-" * 20} Starting {inspect.getframeinfo(inspect.currentframe()).function} case... {"-" * 20}')

        # Set Up Mocks
        # Load mock responses from file
        with open('./tests/mocks/data_crawler/ar-firm-detail-page-abrdn.mock.html', 'r') as _:
            firm_detail_page_response_mock = _.read()

        # Financial Statements Page Request Mock
        self.financial_statements_page_request_mock: ScrapeRequest = MagicMock(ScrapeRequest, metadata={})
        self.financial_statements_page_request_mock.response.text = firm_detail_page_response_mock
        self.financial_statements_page_request_mock.response.request.url = 'http://test.url'

        # HTTP Client Mock
        self.http_client_mock = MagicMock(Client)

    def test_parse_firms_detail_page(self) -> None:
        """Test the parsing of the firms detail page HTML"""

        # Call the method
        response = parse_firms_detail_page(
            self.financial_statements_page_request_mock,
            client=self.http_client_mock
        )

        # Assert
        self.http_client_mock.request.assert_called()
        self.assertTrue(10, self.http_client_mock.request.call_count)
        self.assertTrue(type(response) is ScrapeResponse)
        self.assertTrue(len(response.further_requests) == 10)
        [self.assertTrue(type(r) is ScrapeRequest) for r in response.further_requests]

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {inspect.getframeinfo(inspect.currentframe()).function} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
