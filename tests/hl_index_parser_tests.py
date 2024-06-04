import unittest
from src.data_crawler.hl_index_parser import parse_stock_table

from typing import Dict


class MyTestCase(unittest.TestCase):

    def test_parse_shares(self) -> None:
        with open('./tests/mocks/data_crawler/hl-index.mock.html', 'r') as f:
            mock_response = ''.join([line for line in f.readlines()])
        shares: Dict[str, str] = parse_stock_table(mock_response)
        self.assertEqual(dict, type(shares))
        self.assertEqual(110, len(shares.keys()))


if __name__ == '__main__':
    unittest.main()
