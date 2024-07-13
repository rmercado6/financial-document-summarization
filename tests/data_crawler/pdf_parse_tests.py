import unittest
import logging
import pypdf

from unittest.mock import MagicMock
from io import BytesIO

from src.data_crawler.constants import LOGGING_CONFIG
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.parsers.pdf_parse import parse_pdf_file


# Set up Logger
logging.basicConfig(**LOGGING_CONFIG['testing'])
logger = logging.getLogger('PDF Parse Tests')


class PdfParseTestCase(unittest.TestCase):

    def setUp(self):
        """Set up tests case
        Initiate mocks.
        """
        logger.debug(f'{"-" * 20} Starting {self.__class__.__name__} case... {"-" * 20}')

        # Financial Reports PDF Request Mock
        self.financial_reports_pdf_request_mock: ScrapeResponse = MagicMock(
            ScrapeResponse,
            metadata={
                'data_type': 'annual_report',
                'share': {
                    'title': 'Abrdn plc',
                    'ticker': 'ABRDN',
                    'identifier': 'ABRDN',
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
            self.financial_reports_pdf_request_mock.request.response.content = byte_stream.read()

    def test_parse_financial_reports_pdfs(self) -> None:
        """Test the parsing of the financial reports PDFs"""
        metadata, data, further_requests = parse_pdf_file(
            self.financial_reports_pdf_request_mock
        )
        self.assertTrue(data is None)
        self.assertIsNone(further_requests)
        self.assertTrue(type(metadata) is dict)
        self.assertTrue('src' in metadata.keys())
        self.assertTrue('data_type' in metadata.keys())
        self.assertTrue('share' in metadata.keys())

    def tearDown(self):
        logger.debug(f'{"-" * 20} Ending {self.__class__.__name__} case... {"-" * 20}')


if __name__ == '__main__':
    unittest.main()
