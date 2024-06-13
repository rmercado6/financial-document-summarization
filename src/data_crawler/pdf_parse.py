import pypdf

from logging import getLogger
from io import BytesIO
from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.requests import ScrapeRequest, ScrapeResponse


logger = getLogger(LOGGER_NAME)


def parse_pdf_file(request: ScrapeRequest, client: AsyncClient or None = None) -> ScrapeResponse:
    """Parse financial report PDF file responses into plain text

    :param request: Request data-crawler request containing the request info
    :param client: AsyncClient or None client sent by request consumers, useful if new requests are to be made
    :return: ConsumerResponse object containing the parsed data
    """
    data = ''
    metadata = request.metadata.copy()
    byte_stream = BytesIO(request.response.content)
    pdf_reader = pypdf.PdfReader(byte_stream)

    try:
        logger.debug(f'Starting {request.metadata["share"]["epic"]}\'s HL financial reports PDF file '
                     f'\'{request.metadata["data_type"]}\' download process...')

        for page in pdf_reader.pages:
            data += page.extract_text()

        data = data.encode()
        metadata = {
            'src': request.response.request.url,
            'data_type': request.metadata['data_type'],
            'url_append': '',
            'share': request.metadata['share']
        }

        logger.info(f'Scraped {request.metadata["share"]["epic"]}\'s HL financial reports from PDF file '
                    f'\'{request.metadata["data_type"]}\'.')

    except Exception as e:
        logger.exception(e)
        metadata = request.metadata.copy()

    finally:
        return ScrapeResponse(metadata=metadata, data=data)
