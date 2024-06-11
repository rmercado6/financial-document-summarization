import re

from lxml import etree

from src.data_crawler.requests import Request, ConsumerResponse


def parse_stocks_table(response_text: str) -> dict[str, str]:
    parser = etree.HTMLParser()
    selector = etree.fromstring(response_text, parser)
    data = {}
    for stock in selector.xpath("//table[@class='stockTable']/tbody/tr[@class='table-odd' or @class='table-alt']"):
        e = stock.xpath(".//td")[1]
        name = e.xpath(".//a/text()")[0]
        href = e.xpath(".//a/@href")[0]
        data[name] = href
    return data


def parse_financial_statements_and_reports(request: Request) -> ConsumerResponse:
    parser = etree.HTMLParser()
    selector = etree.fromstring(request.response.text, parser)
    data = {'src': request.response.request.url}

    # Gather annual and interim reports download urls & TODO: Build new requests
    for a in selector.xpath("//div[@class='margin-top tab-content clearfix']//a"):
        data[
            re.sub(
                r'(\n|\t|Download|download)',
                '',
                ''.join(a.xpath('.//text()'))
            ).strip().replace('&amp', 'and').lower().replace(' ', '_')
        ] = a.xpath("@href")[0]

    # Gather financial results tables information
    financial_results_lines = []
    for row in selector.xpath("//div[@id='financials-table-wrapper']/table[contains(@class, 'factsheet-table')]/tbody/tr"):
        class_list = row.xpath("./@class")[0] if row.xpath("./@class") else []
        cell = 'th' if class_list == 'factsheet-head' else 'td'
        financial_results_lines.append([re.sub(r'(\n|\t)+', '', x) for x in row.xpath(f"./{cell}/text()")])
    data['financial_results'] = '\n'.join(['\t'.join(l) for l in financial_results_lines])

    # Gather share information
    share = {
        'title': selector.xpath("//head/meta[@name='Share_Title']/@content")[0],
        'description': selector.xpath("//head/meta[@name='Share_Description']/@content")[0],
        'sedol': selector.xpath("//head/meta[@name='Share_Sedol']/@content")[0],
        'epic': selector.xpath("//head/meta[@name='Share_EPIC']/@content")[0],
        'identifier': selector.xpath("//head/meta[@name='Share_Identifier']/@content")[0],
        'tradeable': selector.xpath("//head/meta[@name='Share_Tradeable']/@content")[0],
    }
    data['share'] = share

    # return data
    return ConsumerResponse(request.metadata.copy(), data, [])
