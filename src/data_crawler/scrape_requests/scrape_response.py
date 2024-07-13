import asyncio
import logging
from io import BytesIO

import pymupdf4llm
from httpx import AsyncClient
from pymupdf import pymupdf

from .scrape_request import ScrapeRequest
from src.data_crawler.constants import LOGGER_NAME


logger = logging.getLogger(LOGGER_NAME)


class ScrapeResponse:
    """ConsumerResponse class
    Wrapper for the scraping responses.
    """
    __request: ScrapeRequest
    __content: bytes
    __metadata: dict
    __data: str or bytes
    __further_requests: list[ScrapeRequest] or None
    __reset_count: int

    def __init__(self, scrape_request: ScrapeRequest):
        self.__request = scrape_request
        self.__content = scrape_request.response.content
        self.__metadata = scrape_request.metadata.copy()
        if 'method' not in self.__metadata:
            self.__metadata['method'] = 'GET'
        self.__data = None
        self.__further_requests = None
        self.__reset_count = 0

    @property
    def request(self):
        return self.__request

    @property
    def content(self):
        return self.__content

    @property
    def metadata(self) -> dict:
        """metadata: dict"""
        return self.__metadata

    @property
    def data(self) -> str or bytes:
        """data: any
        The scraped data.
        """
        return self.__data

    @property
    def further_requests(self) -> list[ScrapeRequest]:
        """further_requests: list[ScrapeRequest]
        List of requests to further scrape, if any were generated during the scraping process.
        """
        return self.__further_requests

    @property
    def url(self):
        return self.request.url

    @property
    def is_redirect(self):
        return self.request.response.is_redirect

    @property
    def is_success(self):
        return self.request.response.is_success

    @property
    def status(self):
        return self.request.response.status_code

    @property
    def headers(self):
        return self.request.response.headers

    @property
    def host(self):
        return self.request.response.request.url.host

    @property
    def scheme(self):
        return self.request.response.request.url.scheme

    @property
    def method(self):
        return self.request.request.method

    @property
    def consumer(self):
        return self.request.consumer

    @property
    async def document(self):
        await asyncio.sleep(0)
        if not self.data and self.content and self.consumer.__name__ == 'parse_pdf_file':
            logger.debug(f'Parsing MD for '
                         f'{self.metadata["share"]["title"]} : {self.metadata["data_type"]} {self.metadata["year"]}')
            byte_stream: BytesIO = BytesIO(self.content)
            document: pymupdf.Document = pymupdf.Document(stream=byte_stream)
            return pymupdf4llm.to_markdown(document)
        if type(self.data) is str:
            return self.data
        elif type(self.data) is bytes:
            return self.data.decode('utf-8')
        return None

    def get_postmortem_log(self, exception: Exception) -> dict:
        try:
            return {
                'type': self.__class__.__name__,
                'response': self.request.response.status_code,
                'metadata': self.metadata,
                'resets': self.__reset_count,
                'exception': str(exception)
            }
        except AttributeError or Exception:
            return {'response': None, 'metadata': self.metadata, 'resets': self.__reset_count}

    def reset(self, client: AsyncClient) -> int:
        self.__reset_count += 1
        return self.__reset_count

    def consume(self, client: AsyncClient):
        metadata, data, further_requests = self.consumer(self, client)
        self.__metadata = metadata
        self.__data = data
        self.__further_requests = further_requests

    async def jsonl(self) -> dict:
        await asyncio.sleep(0)
        return {
            'title': self.metadata['share']['title'],
            'ticker': self.metadata['share']['ticker'],
            'year': self.metadata['year'] if 'year' in self.metadata.keys() else None,
            'document_type': self.metadata['data_type'],
            'doc': await self.document,
        }
