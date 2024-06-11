import re
import pypdf

from httpx import AsyncClient
from lxml import etree
from io import BytesIO

from src.data_crawler.requests import ScrapeRequest, ScrapeResponse


def parse_stocks_table(response_text: str) -> dict[str, str]:
    """Function to parse the stocks table content

    :param response_text: html response text
    :return: dict[str, str] dictionary with the stock name and the url to the stock data page
    """
    parser = etree.HTMLParser()
    selector = etree.fromstring(response_text, parser)
    data = {}
    for stock in selector.xpath("//table[@class='stockTable']/tbody/tr[@class='table-odd' or @class='table-alt']"):
        e = stock.xpath(".//td")[1]
        name = e.xpath(".//a/text()")[0]
        href = e.xpath(".//a/@href")[0]
        data[name] = href
    return data


def parse_financial_statements_and_reports(
        request: ScrapeRequest,
        client: AsyncClient or None = None
) -> ScrapeResponse:
    """Functon to parse the financial statements table contents and obtain the financial reports pdf download links

    :param request: ScrapeRequest Scraping requests.
    :param client: AsyncClient HTTP Client to manage HTTP requests.
    :return: ScrapeResponse response with the scraped information and its metadata.
    """
    parser = etree.HTMLParser()
    selector = etree.fromstring(request.response.text, parser)

    # Gather financial results tables information
    financial_results_lines = []
    for row in selector.xpath(
            "//div[@id='financials-table-wrapper']/table[contains(@class, 'factsheet-table')]/tbody/tr"
    ):
        class_list = row.xpath("./@class")[0] if row.xpath("./@class") else []
        cell = 'th' if class_list == 'factsheet-head' else 'td'
        financial_results_lines.append([re.sub(r'(\n|\t)+', '', x) for x in row.xpath(f"./{cell}/text()")])
    data = '\n'.join(['\t'.join(_) for _ in financial_results_lines])

    # Gather share information
    share = {
        'title': selector.xpath("//head/meta[@name='Share_Title']/@content")[0],
        'description': selector.xpath("//head/meta[@name='Share_Description']/@content")[0],
        'sedol': selector.xpath("//head/meta[@name='Share_Sedol']/@content")[0],
        'epic': selector.xpath("//head/meta[@name='Share_EPIC']/@content")[0],
        'identifier': selector.xpath("//head/meta[@name='Share_Identifier']/@content")[0],
        'tradeable': selector.xpath("//head/meta[@name='Share_Tradeable']/@content")[0],
    }

    # Gather annual and interim reports download urls & Build new requests
    requests = []
    for a in selector.xpath("//div[@class='margin-top tab-content clearfix']/div[@class='grey-gradient clearfix']//a"):
        m = request.metadata.copy()
        m.update({
            'data_type': re.sub(
                r'(\n|\t|Download|download)',
                '',
                ''.join(a.xpath('.//text()'))
            ).strip().replace('&amp', 'and').lower().replace(' ', '_'),
            'url_append': '',
            'share': share
        })
        requests.append(
            ScrapeRequest(
                metadata=m,
                request=client.request(method="GET", url=a.xpath("@href")[0]),
                consumer=parse_financial_reports_pdf_file
            )
        )

    # Build response metadata
    m = request.metadata.copy()
    m.update({
        'src': request.response.request.url,
        'data_type': 'financial_results',
        'url_append': '',
        'share': share
    })

    # return data
    return ScrapeResponse(m, data, requests)


def parse_financial_reports_pdf_file(request: ScrapeRequest, client: AsyncClient or None = None) -> ScrapeResponse:
    """Parse financial report PDF file responses into plain text

    :param request: Request data-crawler request containing the request info
    :param client: AsyncClient or None client sent by request consumers, useful if new requests are to be made
    :return: ConsumerResponse object containing the parsed data
    """
    data = ''
    byte_stream = BytesIO(request.response.content)
    pdf_reader = pypdf.PdfReader(byte_stream)
    for page in pdf_reader.pages:
        data += page.extract_text()

    return ScrapeResponse(
        metadata={
            'src': request.response.request.url,
            'data_type': request.metadata['data_type'],
            'url_append': '',
            'share': request.metadata['share']
        },
        data=data
    )
