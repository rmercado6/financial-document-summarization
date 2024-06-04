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
    return
