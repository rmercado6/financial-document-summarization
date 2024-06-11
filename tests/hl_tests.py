import unittest
import httpx
import pypdf

from io import BytesIO
from unittest import TestCase, IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_parse import (parse_stocks_table, parse_financial_statements_and_reports,
                                       parse_financial_reports_pdf_file)
from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.requests import Request, ConsumerResponse


with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as f:
    stocks_table_mock_response = f.read()

with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as f:
    financial_statements_page_mock_response = f.read()

with open('./tests/mocks/data_crawler/hl-financial-reports-abrdn.mock.pdf', 'rb') as f:
    pdf_reader = pypdf.PdfReader(f)
    pdf_writer = pypdf.PdfWriter()
    pdf_writer.add_page(pdf_reader.get_page(0))
    byte_stream = BytesIO()
    pdf_writer.write_stream(byte_stream)
    byte_stream.seek(0)
    financial_report_pdf_mock_response = byte_stream.read()


class HlParseTests(TestCase):

    def setUp(self):
        self.financial_statements_page_mock_request: Request = MagicMock(Request, metadata={})
        self.financial_statements_page_mock_request.response.text = financial_statements_page_mock_response
        self.financial_statements_page_mock_request.response.request.url = 'http://test.url'

        self.mock_client = MagicMock()

        self.financial_reports_pdf_mock_request: Request = MagicMock(
            Request,
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
        self.financial_reports_pdf_mock_request.response.content = financial_report_pdf_mock_response

    def test_parse_stocks_table(self) -> None:
        stocks: dict[str, str] = parse_stocks_table(stocks_table_mock_response)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def test_parse_financial_statements_and_reports(self) -> None:
        response: ConsumerResponse = parse_financial_statements_and_reports(
            self.financial_statements_page_mock_request,
            client=self.mock_client
        )
        self.assertTrue(type(response) is ConsumerResponse)
        self.assertTrue(type(response.metadata) is dict)
        self.assertTrue(type(response.data) is dict)
        self.assertTrue(type(response.further_requests) is list)
        self.assertGreaterEqual(len(response.data.keys()), 3)

        # Assert the inclusion of information source in response
        self.assertTrue('src' in response.data.keys())
        self.assertEqual('http://test.url', response.data['src'])

        # Assert the inclusion of the scraped financial results reports tables
        self.assertTrue('financial_results' in response.data.keys())

        # Assert the inclusion of the scraped share information
        self.assertTrue('share' in response.data.keys())
        self.assertTrue('title' in response.data['share'].keys())
        self.assertTrue('description' in response.data['share'].keys())
        self.assertTrue('sedol' in response.data['share'].keys())
        self.assertTrue('epic' in response.data['share'].keys())
        self.assertTrue('identifier' in response.data['share'].keys())

        # Assert the extraction of PDF report urls
        self.assertGreaterEqual(len(response.further_requests), 2)
        for r in response.further_requests:
            self.assertTrue(type(r) is Request)
            self.assertTrue('url_append' in r.metadata.keys())
            self.assertTrue('data_type' in r.metadata.keys())

    def test_parse_financial_reports_pdfs(self) -> None:
        response: ConsumerResponse = parse_financial_reports_pdf_file(
            self.financial_reports_pdf_mock_request
        )
        self.assertTrue(type(response) is ConsumerResponse)
        self.assertTrue(type(response.data) is str)
        self.assertIsNone(response.further_requests)
        self.assertTrue(type(response.metadata) is dict)
        self.assertTrue('src' in response.metadata.keys())
        self.assertTrue('data_type' in response.metadata.keys())
        self.assertTrue('share' in response.metadata.keys())


class HlScrapeStocksTableTest(IsolatedAsyncioTestCase):

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_scrape_hl_index_stocks_table(self, async_client_mock: AsyncMock) -> None:
        # Set up Mocks
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=stocks_table_mock_response
        )

        # Call method
        r = await scrape_hl_index_stocks_table('', 1)

        # Assert Method
        async_client_mock.assert_awaited_once_with("?page=1")
        self.assertEqual(dict, type(r))
        self.assertEqual(110, len(r.keys()))
        self.assertTrue('Abrdn plc' in r.keys())


class HlScrapeFinancialStatementsPageTest(IsolatedAsyncioTestCase):

    def setUp(self):
        # Set mock request
        self.mock_request = MagicMock(httpx.Request, method='GET', url='http://test.url')

        # Set pdf response contents
        writer = pypdf.PdfWriter()
        writer.add_blank_page(100, 100)
        byte_stream = BytesIO()
        writer.write_stream(byte_stream)
        byte_stream.seek(0)
        self.pdf_content = byte_stream.read()

    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    async def test_scrape_hl_index_stock_pages(self, async_client_mock: AsyncMock) -> None:
        # Set Up Mocks
        async_client_mock.side_effect = [
            httpx.Response(200, content=financial_statements_page_mock_response, request=self.mock_request),
            httpx.Response(200, content=self.pdf_content, request=self.mock_request),
            httpx.Response(200, content=self.pdf_content, request=self.mock_request)
        ]

        # Call function
        await scrape_hl_index_stock_pages({
            'Abrdn plc': '/shares/shares-search-results/BF8Q6K6',
        })

        self.assertEqual(3, async_client_mock.await_count)


if __name__ == '__main__':
    unittest.main()
