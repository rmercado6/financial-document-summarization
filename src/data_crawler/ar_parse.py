from logging import getLogger

from httpx import AsyncClient
from lxml import etree

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.scrape_requests.requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.pdf_parse import parse_pdf_file


logger = getLogger(LOGGER_NAME)


def parse_stocks_table(response_text: str) -> dict[str, str]:
    """Function to parse the stocks table content

    :param response_text: html response text
    :return: dict[str, str] dictionary with the stock name and the url to the stock data page
    """
    logger.debug('Starting AR\'s stock table parsing process...')

    parser = etree.HTMLParser()
    selector = etree.fromstring(response_text, parser)
    data = {}
    for stock in selector.xpath("//div[@class='apparel_stores_company_list']//span[@class='companyName']/a"):
        name = stock.xpath("./text()")[0]
        href = stock.xpath("./@href")[0]
        data[name] = href

    logger.debug('Finished AR\'s stock table parsing process.')

    return data


def parse_firms_detail_page(
        request: ScrapeRequest,
        client: AsyncClient or None = None
) -> ScrapeResponse:
    """Functon to parse the firm's detail page to get the financial reports pdf download links

    :param request: ScrapeRequest request object.
    :param client: Httpx AsyncClient HTTP Client to manage HTTP requests.
    :return: None
    """
    logger.debug(f'Starting AR\'s firms detail parsing for {request.response.request.url}...')

    parser = etree.HTMLParser()
    selector = etree.fromstring(request.response.text, parser)

    # Gather share information
    share = {
        'title': selector.xpath("//div[@class='left_section']/div[@class='vendor_name']/h1/text()")[0],
        'ticker': selector.xpath("//span[@class='ticker_name']/text()")[0],
        'identifier': selector.xpath("//span[@class='ticker_name']/text()")[0],
    }

    logger.debug(f'Gathered stock metadata from {request.response.request.url}.')

    # Gather annual and interim reports download urls & Build new requests
    requests = []
    for div in selector.xpath("//div[@class='archived_report_content_block']/ul/li/div"):
        m = request.metadata.copy()
        m.update({
            'data_type': 'annual_report',
            'year': div.xpath("./span[@class='heading']/@text"),
            'url_append': '',
            'share': share
        })
        requests.append(
            ScrapeRequest(
                metadata=m,
                request=client.request(method="GET", url=div.xpath("/span[@class='btn_archived download']/a/@href")),
                consumer=parse_pdf_file
            )
        )
    logger.debug(f'Built requests for annual and interim reports download urls for {request.response.request.url}.')

    # Build response metadata
    m = request.metadata.copy()
    m.update({
        'src': request.response.request.url,
        'data_type': 'None',
        'url_append': '',
        'share': share
    })

    logger.info(f'Scraped {share["ticker"]}\'s AR detail page.')

    # return data
    return ScrapeResponse(m, None, requests)

