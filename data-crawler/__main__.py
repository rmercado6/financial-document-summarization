import asyncio
from lxml import etree
from httpx import AsyncClient, Response


N_PAGES = 6

BASE_URLS = {
    'hl-index': 'https://www.hl.co.uk/shares/stock-market-summary/ftse-all-share'
}

__client = AsyncClient(
    headers={
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    }
)


def parse_shares(response: Response) -> dict:
    parser = etree.HTMLParser()
    selector = etree.fromstring(response.text, parser)
    data = {}
    for share in selector.xpath("//table[@class='stockTable']/tbody/tr[@class='table-odd' or @class='table-alt']"):
        e = share.xpath(".//td")[1]
        name = e.xpath(".//a/text()")[0]
        href = e.xpath(".//a/@href")[0]
        data[name] = href
    return data


async def scrape(url: str) -> dict:
    __shares = {}
    pages = [__client.get(url + f"?page={page_number}") for page_number in range(1, )]
    for response in asyncio.as_completed(pages):
        response = await response
        data = parse_shares(response)
        __shares.update(data)
    return __shares


if __name__ == '__main__':
    shares = asyncio.run(scrape(BASE_URLS['hl-index']))
    print('Done')
