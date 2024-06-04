from lxml import etree


def parse_stock_table(response: str) -> dict[str, str]:
    parser = etree.HTMLParser()
    selector = etree.fromstring(response, parser)
    data = {}
    for share in selector.xpath("//table[@class='stockTable']/tbody/tr[@class='table-odd' or @class='table-alt']"):
        e = share.xpath(".//td")[1]
        name = e.xpath(".//a/text()")[0]
        href = e.xpath(".//a/@href")[0]
        data[name] = href
    return data



