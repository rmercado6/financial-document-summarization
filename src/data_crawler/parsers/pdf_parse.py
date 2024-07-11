from logging import getLogger
from httpx import AsyncClient

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse

logger = getLogger(LOGGER_NAME)


def parse_pdf_file(
        response: ScrapeResponse,
        client: AsyncClient or None = None
) -> tuple[dict, str or bytes, list[ScrapeRequest] or None]:
    """Parse financial report PDF file responses into plain text

    :param response: Request data-crawler request containing the request info
    :param client: AsyncClient or None client sent by request consumers, useful if new requests are to be made
    :return: ConsumerResponse object containing the parsed data
    """
    metadata: dict = response.metadata.copy()
    try:
        logger.debug(f'Starting {response.metadata["share"]["ticker"]}\'s financial reports PDF file '
                     f'\'{response.metadata["data_type"]}\' download process...')

        metadata = {
            'src': response.url,
            'data_type': response.metadata['data_type'],
            'url_append': '',
            'share': response.metadata['share'],
            'year': response.metadata['year'] if 'year' in response.metadata.keys() else None,
        }

        logger.info(f'Scraped {response.metadata["share"]["ticker"]}\'s financial reports from PDF file '
                    f'\'{response.metadata["data_type"]}\'.')

    except Exception as e:
        logger.exception(e)
        metadata = response.metadata.copy()

    finally:
        return metadata, None, None
