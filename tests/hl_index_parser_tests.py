import unittest
from src.data_crawler.hl_index_parser import parse_stock_table

from typing import Dict


class MyTestCase(unittest.TestCase):

    def test_parse_stock_table(self) -> None:
        with open('./tests/mocks/data_crawler/hl-index.mock.html', 'r') as f:
            mock_response = ''.join([line for line in f.readlines()])
        stocks: Dict[str, str] = parse_stock_table(mock_response)
        self.assertEqual(dict, type(stocks))
        self.assertEqual(110, len(stocks.keys()))


if __name__ == '__main__':
    unittest.main()
