import unittest
import logging

from unittest.mock import MagicMock

from src.data_crawler.constants import LOGGING_CONFIG
from src.data_crawler.requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.ar_parse import parse_stocks_table, parse_firms_detail_page


# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('AR Parse Tests')


class ARParseTests(unittest.TestCase):
    """Test the different methods for parsing information from AnnualReports"""

    def setUp(self):
        """Set up tests case
        Initiate mocks.
        """
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load mock responses from files
        with open('./tests/mocks/data_crawler/ar-stocks-table.mock.html', 'r') as _:
            self.stocks_table_response_mock = _.read()

        with open('./tests/mocks/data_crawler/ar-firm-detail-page-abrdn.mock.html', 'r') as _:
            firm_detail_page_response_mock = _.read()

        # Financial Statements Page Request Mock
        self.financial_statements_page_request_mock: ScrapeRequest = MagicMock(ScrapeRequest, metadata={})
        self.financial_statements_page_request_mock.response.text = firm_detail_page_response_mock
        self.financial_statements_page_request_mock.response.request.url = 'http://test.url'

        # HTTP Client Mock
        self.http_client_mock = MagicMock()

    def test_parse_stocks_table(self) -> None:
        """Test the parsing of the stocks table HTML"""
        stocks: dict[str, str] = parse_stocks_table(self.stocks_table_response_mock)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/Company/4imprint-group-plc', stocks['4imprint Group plc'])

    def test_parse_firms_detail_page(self) -> None:
        """Test the parsing of the firms detail page HTML"""
        response = parse_firms_detail_page(
            self.financial_statements_page_request_mock,
            client=self.http_client_mock
        )
        self.http_client_mock.assert_called_once()
        self.assertTrue(type(response) is ScrapeResponse)
        self.assertTrue(len(response.further_requests) == 10)
        [self.assertTrue(type(r) is ScrapeRequest) for r in response.further_requests]

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
