import jsonlines
import pymupdf
import pymupdf4llm
# import httpx

# from io import BytesIO

from src.data_crawler.scrape_requests.requests import ScrapeResponse


data: bytes
metadata: dict

# REMOTE FILES
# url = 'https://www.annualreports.com/HostedData/AnnualReportArchive/1/LSE_SPA_2022.pdf'
# response = httpx.get(url)
# byte_stream = BytesIO(response.content)
# doc = pymupdf.open(stream=byte_stream)

# LOCAL FILES
doc = pymupdf.open('tests/mocks/pdf_converter/annual report.pdf')
md_text = pymupdf4llm.to_markdown(doc)

data = md_text.encode()
metadata = {    # Build fake metadata
    'src': '',
    'data_type': '',
    'url_append': '',
    'share': {
        'title': '',
        'ticker': '',
        'identifier': '',
    },
    'year': '',
}

response = ScrapeResponse(metadata=metadata, data=data)

with jsonlines.open('out/pdf_converter/file.jsonl', 'a') as _:
    _.write(response.jsonl())
