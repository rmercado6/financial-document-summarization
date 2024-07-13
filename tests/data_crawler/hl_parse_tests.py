import unittest
import logging

from unittest.mock import MagicMock

from src.data_crawler.constants import LOGGING_CONFIG
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.parsers.hl_parse import parse_stocks_table, parse_financial_statements_and_reports


# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('HL Parse Tests')


class HlParseFinancialStatementsAndReportsTestCase(unittest.TestCase):

    def setUp(self):
        """Set up tests case
        Initiate mocks.
        """
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load Mock responses from files
        with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as _:
            financial_statements_page_response_mock = _.read()

        # Financial Statements Page Request Mock
        self.financial_statements_page_request_mock: ScrapeResponse = MagicMock(ScrapeResponse, metadata={})
        self.financial_statements_page_request_mock.request.response.text = financial_statements_page_response_mock
        self.financial_statements_page_request_mock.url = 'http://test.url'

        # HTTP Client Mock
        self.http_client_mock = MagicMock()

    def test_parse_financial_statements_and_reports(self) -> None:
        """Test the parsing of the financial statements and reports HTML"""
        metadata, data, further_requests = parse_financial_statements_and_reports(
            self.financial_statements_page_request_mock,
            client=self.http_client_mock
        )
        self.assertTrue(type(metadata) is dict)
        self.assertTrue(type(data) is bytes)
        self.assertTrue(type(further_requests) is list)
        self.assertGreaterEqual(len(metadata.keys()), 4)

        # Assert the inclusion of information source in response
        self.assertTrue('src' in metadata.keys())
        self.assertEqual('http://test.url', metadata['src'])

        # Assert the inclusion of the scraped share information
        self.assertTrue('share' in metadata.keys())
        self.assertTrue('title' in metadata['share'].keys())
        self.assertTrue('ticker' in metadata['share'].keys())
        self.assertTrue('identifier' in metadata['share'].keys())

        # Assert the extraction of PDF report urls
        self.assertGreaterEqual(len(further_requests), 2)
        for r in further_requests:
            self.assertTrue(type(r) is ScrapeRequest)
            self.assertTrue('url_append' in r.metadata.keys())
            self.assertTrue('data_type' in r.metadata.keys())

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


class HlParseStocsTableTestCase(unittest.TestCase):
    """Test the different methods for parsing information from HL"""

    def setUp(self):
        """Set up tests case
        Initiate mocks.
        """
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Load Mock responses from files
        with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as _:
            self.stocks_table_response_mock = _.read()

    def test_parse_stocks_table(self) -> None:
        """Test the parsing of the stocks table HTML"""
        stocks: dict[str, str] = parse_stocks_table(self.stocks_table_response_mock)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
