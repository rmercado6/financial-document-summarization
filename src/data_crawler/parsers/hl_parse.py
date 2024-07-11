import logging
import re

from httpx import AsyncClient
from lxml import etree
from datetime import datetime
from markdownify import markdownify as md

from src.data_crawler.constants import LOGGER_NAME
from src.data_crawler.scrape_requests import ScrapeRequest, ScrapeResponse
from src.data_crawler.parsers.pdf_parse import parse_pdf_file


logger = logging.getLogger(LOGGER_NAME)


def parse_stocks_table(response_text: str) -> dict[str, str]:
    """Function to parse the stocks table content

    :param response_text: html response text
    :return: dict[str, str] dictionary with the stock name and the url to the stock data page
    """
    logger.debug('Starting HL\'s stock table parsing process...')

    parser = etree.HTMLParser()
    selector = etree.fromstring(response_text, parser)
    data = {}
    for stock in selector.xpath("//table[@class='stockTable']/tbody/tr[@class='table-odd' or @class='table-alt']"):
        e = stock.xpath(".//td")[1]
        name = e.xpath(".//a/text()")[0]
        href = e.xpath(".//a/@href")[0]
        data[name] = href

    logger.debug('Finished HL\'s stock table parsing process.')

    return data


def parse_financial_statements_and_reports(
        response: ScrapeResponse,
        client: AsyncClient or None = None
) -> tuple[dict, str or bytes, list[ScrapeRequest] or None]:
    """Functon to parse the financial statements table contents and obtain the financial reports pdf download links

    :param response: ScrapeRequest Scraping requests.
    :param client: AsyncClient HTTP Client to manage HTTP requests.
    :return: ScrapeResponse response with the scraped information and its metadata.
    """
    logger.debug(f'Starting HL\'s financial statements table parsing for {response.url}...')

    parser = etree.HTMLParser()
    selector = etree.fromstring(response.request.response.text, parser)

    # Gather share information
    share = {
        'title': selector.xpath("//head/meta[@name='Share_Title']/@content")[0],
        'ticker': selector.xpath("//head/meta[@name='Share_EPIC']/@content")[0],
        'identifier': selector.xpath("//head/meta[@name='Share_Identifier']/@content")[0],
    }

    logger.debug(f'Gathered stock metadata from {response.url}.')

    # Gather financial results tables information
    data = None
    try:
        financials_table = selector.xpath("//div[@id='financials-table-wrapper']")
        inner_html = etree.tostring(financials_table[0]).decode().replace('&#13;', '')
        markdown = md(inner_html)
        data = markdown.encode()
        logger.debug(f'Gathered HL financial reports table for {response.url}.')
    except Exception:
        logger.warning(f'No financial results table found for {share["ticker"]} @ {response.url}.')

    # Gather annual and interim reports download urls & Build new requests
    requests = []
    links = selector.xpath("//div[@class='margin-top tab-content clearfix']/div[@class='grey-gradient clearfix']//a")
    if len(links) > 0:
        for a in links:
            url = a.xpath("@href")[0]
            m = response.metadata.copy()
            m.update({
                'data_type': re.sub(
                    r'(\n|\t|Download|download)',
                    '',
                    ''.join(a.xpath('.//text()'))
                ).split('&amp')[0].strip().lower().replace(' ', '_'),
                'url_append': '',
                'year': datetime.now().year - 1,
                'share': share,
                'url': url,
                'method': 'GET'
            })
            requests.append(
                ScrapeRequest(
                    metadata=m,
                    request=client.request(method="GET", url=url),
                    consumer=parse_pdf_file
                )
            )
        logger.debug(f'Built requests for annual and interim reports download urls for {response.url}.')
    else:
        logger.warning(f'No annual reports found for {share["ticker"]} @ {response.url}.')

    # Build response metadata
    m = response.metadata.copy()
    m.update({
        'src': response.url,
        'data_type': 'financial_results',
        'url_append': '',
        'share': share,
        'year': f'{datetime.now().year - 5}-{datetime.now().year - 1}',
    })

    logger.info(f'Scraped {share["ticker"]}\'s financial statement and reports table.')

    # return data
    return m, data, requests



