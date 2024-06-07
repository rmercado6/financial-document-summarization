import re

from lxml import etree


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


def parse_financial_statements_and_reports(response_text: str) -> dict[str, str]:
    parser = etree.HTMLParser()
    selector = etree.fromstring(response_text, parser)
    data = {}

    # Gather annual and interim reports download urls
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

    return data
