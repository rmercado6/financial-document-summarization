import unittest
import httpx

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.requests import Request, ConsumerResponse


with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as f:
    stocks_table_mock_response = ''.join([line for line in f.readlines()])

with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as f:
    financial_statements_page_mock_response = ''.join([line for line in f.readlines()])


class HlParseTests(unittest.TestCase):

    def setUp(self):
        self.financial_statements_page_mock_request: Request = MagicMock(Request, metadata={})
        self.financial_statements_page_mock_request.response.text = financial_statements_page_mock_response
        self.financial_statements_page_mock_request.response.request.url = 'http://test.url'

    def test_parse_stocks_table(self) -> None:
        stocks: dict[str, str] = parse_stocks_table(stocks_table_mock_response)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def test_parse_financial_statements_and_reports(self) -> None:
        response: ConsumerResponse = parse_financial_statements_and_reports(self.financial_statements_page_mock_request)
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


class HlScrapeStocksTableTest(IsolatedAsyncioTestCase):

    @patch('httpx.AsyncClient.get', new_callable=AsyncMock)
    async def test_scrape_hl_index_stocks_table(self, async_client_mock: AsyncMock) -> None:
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=stocks_table_mock_response
        )

        r = await scrape_hl_index_stocks_table('', 1)

        async_client_mock.assert_awaited_once_with("?page=1")
        self.assertEqual(dict, type(r))
        self.assertEqual(110, len(r.keys()))
        self.assertTrue('Abrdn plc' in r.keys())


class HlScrapeFinancialStatementsPageTest(unittest.IsolatedAsyncioTestCase):

    @patch('httpx.AsyncClient.request', new_callable=AsyncMock)
    async def test_scrape_hl_index_stock_pages(self, async_client_mock: AsyncMock) -> None:
        async_client_mock.return_value = httpx.Response(
            status_code=200,
            content=financial_statements_page_mock_response,
            request=httpx.Request(method='GET', url='')
        )

        await scrape_hl_index_stock_pages({
            'Abrdn plc': '/shares/shares-search-results/BF8Q6K6',
        })

        async_client_mock.assert_awaited()


if __name__ == '__main__':
    unittest.main()
