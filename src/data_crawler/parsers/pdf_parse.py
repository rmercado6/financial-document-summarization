import pymupdf
import pymupdf4llm

from logging import getLogger
from io import BytesIO
from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse

logger = getLogger(LOGGER_NAME)


def parse_pdf_file(request: ScrapeRequest, client: AsyncClient or None = None) -> ScrapeResponse:
    """Parse financial report PDF file responses into plain text

    :param request: Request data-crawler request containing the request info
    :param client: AsyncClient or None client sent by request consumers, useful if new requests are to be made
    :return: ConsumerResponse object containing the parsed data
    """
    data: bytes = b''
    metadata: dict = request.metadata.copy()
    byte_stream: BytesIO = BytesIO(request.response.content)
    document: pymupdf.Document = pymupdf.Document(stream=byte_stream)

    try:
        logger.debug(f'Starting {request.metadata["share"]["ticker"]}\'s financial reports PDF file '
                     f'\'{request.metadata["data_type"]}\' download process...')

        md_text = pymupdf4llm.to_markdown(document)

        data = md_text.encode()
        metadata = {
            'src': request.url,
            'data_type': request.metadata['data_type'],
            'url_append': '',
            'share': request.metadata['share'],
            'year': request.metadata['year'] if 'year' in request.metadata.keys() else None,
        }

        logger.info(f'Scraped {request.metadata["share"]["ticker"]}\'s financial reports from PDF file '
                    f'\'{request.metadata["data_type"]}\'.')

    except Exception as e:
        logger.exception(e)
        metadata = request.metadata.copy()

    finally:
        return ScrapeResponse(metadata=metadata, data=data)
