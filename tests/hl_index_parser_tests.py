import unittest
from src.data_crawler.hl_parse import parse_stocks_table, parse_financial_statements_and_reports


class HlIndexParserTests(unittest.TestCase):

    def test_parse_stocks_table(self) -> None:
        with open('./tests/mocks/data_crawler/hl-index.mock.html', 'r') as f:
            mock_response = ''.join([line for line in f.readlines()])
        stocks: dict[str, str] = parse_stocks_table(mock_response)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))
        self.assertEqual('/shares/shares-search-results/0664097', stocks['4imprint Group plc'])

    def test_parse_financial_statements_and_reports(self) -> None:
        with open('./tests/mocks/data_crawler/hl-index-financial-statements-abrdn.mock.html', 'r') as f:
            mock_response = ''.join([line for line in f.readlines()])
        fin_data: dict[str, str] = parse_financial_statements_and_reports(mock_response)
        self.assertEqual(dict, type(fin_data))


if __name__ == '__main__':
    unittest.main()
