import unittest
import httpx
import pypdf

from io import BytesIO
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_parse import (parse_stocks_table, parse_financial_statements_and_reports,
                                       parse_financial_reports_pdf_file)
from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.requests import ScrapeRequest, ScrapeResponse


# Start reusable MOCKS
with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as _:
    stocks_table_response_mock = _.read()

with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as _:
    financial_statements_page_response_mock = _.read()


class HlParseTests(TestCase):
    """Test the different methods for parsing information from HL"""

    def setUp(self):
        """Set up tests case
        Initiate mocks.
        """
        # Financial Statements Page Request Mock
        self.financial_statements_page_request_mock: ScrapeRequest = MagicMock(ScrapeRequest, metadata={})
        self.financial_statements_page_request_mock.response.text = financial_statements_page_response_mock
        self.financial_statements_page_request_mock.response.request.url = 'http://test.url'

        # HTTP Client Mock
        self.http_client_mock = MagicMock()

        # Financial Reports PDF Request Mock
        self.financial_reports_pdf_request_mock: ScrapeRequest = MagicMock(
            ScrapeRequest,
            metadata={
                'data_type': 'annual_report',
                'share': {
                    'title': 'Abrdn plc',
                    'description': 'abrdn',
                    'sedol': '123456',
                    'epic': 'ABRDN',
                    'identifier': 'ABRDN',
                    'tradeable': 'yes',
                }
            }
        )

        # Load pdf response [first page only]
        with open('./tests/mocks/data_crawler/hl-financial-reports-abrdn.mock.pdf', 'rb') as _:
            pdf_reader = pypdf.PdfReader(_)
            pdf_writer = pypdf.PdfWriter()
            pdf_writer.add_page(pdf_reader.get_page(0))
            byte_stream = BytesIO()
            pdf_writer.write_stream(byte_stream)
            byte_stream.seek(0)
            self.financial_reports_pdf_request_mock.response.content = byte_stream.read()

    def test_parse_stocks_table(self) -> None:
        """Test the parsing of the stocks table HTML"""
        stocks: dict[str, str] = parse_stocks_table(stocks_table_response_mock)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def test_parse_financial_statements_and_reports(self) -> None:
        """Test the parsing of the financial statements and reports HTML"""
        response: ScrapeResponse = parse_financial_statements_and_reports(
            self.financial_statements_page_request_mock,
            client=self.http_client_mock
        )
        self.assertTrue(type(response) is ScrapeResponse)
        self.assertTrue(type(response.metadata) is dict)
        self.assertTrue(type(response.data) is bytes)
        self.assertTrue(type(response.further_requests) is list)
        self.assertGreaterEqual(len(response.metadata.keys()), 4)

        # Assert the inclusion of information source in response
        self.assertTrue('src' in response.metadata.keys())
        self.assertEqual('http://test.url', response.metadata['src'])

        # Assert the inclusion of the scraped share information
        self.assertTrue('share' in response.metadata.keys())
        self.assertTrue('title' in response.metadata['share'].keys())
        self.assertTrue('description' in response.metadata['share'].keys())
        self.assertTrue('sedol' in response.metadata['share'].keys())
        self.assertTrue('epic' in response.metadata['share'].keys())
        self.assertTrue('identifier' in response.metadata['share'].keys())

        # Assert the extraction of PDF report urls
        self.assertGreaterEqual(len(response.further_requests), 2)
        for r in response.further_requests:
            self.assertTrue(type(r) is ScrapeRequest)
            self.assertTrue('url_append' in r.metadata.keys())
            self.assertTrue('data_type' in r.metadata.keys())

    def test_parse_financial_reports_pdfs(self) -> None:
        """Test the parsing of the financial reports PDFs"""
        response: ScrapeResponse = parse_financial_reports_pdf_file(
            self.financial_reports_pdf_request_mock
        )
        self.assertTrue(type(response) is ScrapeResponse)
        self.assertTrue(type(response.data) is bytes)
        self.assertIsNone(response.further_requests)
        self.assertTrue(type(response.metadata) is dict)
        self.assertTrue('src' in response.metadata.keys())
        self.assertTrue('data_type' in response.metadata.keys())
        self.assertTrue('share' in response.metadata.keys())


class HlScrapeStocksTableTest(IsolatedAsyncioTestCase):
    """Asynchronous test case for testing the scraping of the stocks table"""

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_scrape_hl_index_stocks_table(self, async_client_mock: AsyncMock) -> None:
        """Test the scraping of the stocks table"""
        # Set up Mocks
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=stocks_table_response_mock
        )

        # Call method
        r = await scrape_hl_index_stocks_table('', 1)

        # Assert
        async_client_mock.assert_awaited_once_with("?page=1")
        self.assertEqual(dict, type(r))
        self.assertEqual(110, len(r.keys()))
        self.assertTrue('Abrdn plc' in r.keys())


class HlScrapeFinancialStatementsPageTest(IsolatedAsyncioTestCase):
    """Test the scraping of the financial statements page"""

    def setUp(self):
        # Set mock request
        self.request_mock = MagicMock(httpx.Request, method='GET', url='http://test.url')

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
            httpx.Response(200, content=financial_statements_page_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock),
            httpx.Response(200, content=self.pdf_response_mock, request=self.request_mock)
        ]

        # Call function
        await scrape_hl_index_stock_pages({
            'Abrdn plc': '/shares/shares-search-results/BF8Q6K6',
        })

        # Assert
        self.assertEqual(3, async_client_mock.await_count)


if __name__ == '__main__':
    unittest.main()
