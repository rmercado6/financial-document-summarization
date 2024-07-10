from logging import getLogger

from httpx import AsyncClient
from lxml import etree

from src.data_crawler.constants import LOGGER_NAME, DATA_SRC_URLS
from src.data_crawler.scrape_requests.requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.parsers.pdf_parse import parse_pdf_file


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
    logger.debug(f'Starting AR\'s firms detail parsing for {request.url}...')

    parser = etree.HTMLParser()
    selector = etree.fromstring(request.response.text, parser)

    # Gather share information
    share = {
        'title': selector.xpath("//div[@class='left_section']/div[@class='vendor_name']/h1/text()")[0],
        'ticker': selector.xpath("//span[@class='ticker_name']/text()")[0],
        'identifier': selector.xpath("//span[@class='ticker_name']/text()")[0],
    }

    logger.debug(f'Gathered stock metadata for {share["ticker"]} from {request.url}.')

    # Gather annual and interim reports download urls & Build new requests
    requests = []
    for div in selector.xpath("//div[@class='archived_report_content_block']/ul/li/div"):
        url = DATA_SRC_URLS['ar-base'] + div.xpath("./span[@class='btn_archived download']/a/@href")[0]
        m = request.metadata.copy()
        m.update({
            'data_type': 'annual_report',
            'year': div.xpath("./span[@class='heading']/text()")[0].split(' ')[0],
            'url_append': None,
            'share': share,
            'url': url,
            'method': 'GET'
        })
        requests.append(
            ScrapeRequest(
                metadata=m,
                request=client.request(
                    method="GET",
                    url=url
                ),
                consumer=parse_pdf_file
            )
        )

    logger.debug(f'Built requests for annual and interim reports download urls for {share["ticker"]} '
                 f'from {request.url}.')

    # Build response metadata
    m = request.metadata.copy()
    m.update({
        'src': request.url,
        'data_type': 'None',
        'url_append': None,
        'share': share,
        'year': None,
    })

    logger.info(f'Scraped {share["ticker"]}\'s AR detail page.')

    # return data
    return ScrapeResponse(m, None, requests)

