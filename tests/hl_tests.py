import unittest
import httpx

from unittest import IsolatedAsyncioTestCase
from unittest.mock import patch, MagicMock, AsyncMock

from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports
from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages


with open('./tests/mocks/data_crawler/hl-stocks-table.mock.html', 'r') as f:
    stocks_table_mock_response = ''.join([line for line in f.readlines()])

with open('./tests/mocks/data_crawler/hl-financial-statements-abrdn.mock.html', 'r') as f:
    financial_statements_page_mock_response = ''.join([line for line in f.readlines()])


class HlParseTests(unittest.TestCase):

    def test_parse_stocks_table(self) -> None:
        stocks: dict[str, str] = parse_stocks_table(stocks_table_mock_response)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def test_parse_financial_statements_and_reports(self) -> None:
        fin_data: dict[str, str] = parse_financial_statements_and_reports(financial_statements_page_mock_response)
        self.assertEqual(dict, type(fin_data))
        self.assertGreaterEqual(3, len(fin_data.keys()))
        self.assertTrue('annual_report_and_accounts' in fin_data.keys())
        self.assertTrue('interim_report_and_accounts' in fin_data.keys())
        self.assertTrue('financial_results' in fin_data.keys())


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
            content=financial_statements_page_mock_response
        )

        r = await scrape_hl_index_stock_pages({
            'Abrdn plc': '/shares/shares-search-results/BF8Q6K6',
        })

        async_client_mock.assert_awaited()


if __name__ == '__main__':
    unittest.main()
