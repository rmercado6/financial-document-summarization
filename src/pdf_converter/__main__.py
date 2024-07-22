import jsonlines
import httpx
import pymupdf
import pymupdf4llm
import asyncio

from pathlib import Path
from io import BytesIO

from src.pdf_converter.cli import get_args
from src.data_crawler.scrape_requests import ScrapeResponse

DEFAULT_OUTPUT_PATH = './data'


async def main(
        path: str,
        title: str,
        ticker: str,
        document_type: str,
        year: str,
        output_path: str = DEFAULT_OUTPUT_PATH,
        remote: bool = False,
):
    data: bytes
    metadata: dict

    Path(output_path).mkdir(parents=True, exist_ok=True)

    if not remote:
        doc = pymupdf.open(path)
    else:
        response = httpx.get(path)
        byte_stream = BytesIO(response.content)
        doc = pymupdf.open(stream=byte_stream)

    md_text = pymupdf4llm.to_markdown(doc)

    data = md_text.encode()
    metadata = {  # Build metadata
        'src': path,
        'data_type': document_type,
        'url_append': '',
        'share': {
            'title': title,
            'ticker': ticker,
            'identifier': '',
        },
        'year': year,
    }

    response = ScrapeResponse(metadata=metadata, data=data)

    output_file = 'documents.jsonl'

    if not output_path.endswith('/'):
        output_file = '/' + output_file

    with jsonlines.open(output_path + output_file, 'a') as _:
        _.write(await response.jsonl())


if __name__ == '__main__':
    args = get_args()
    asyncio.run(
        main(
            args.path,
            args.title,
            args.ticker,
            args.document_type,
            args.year,
            output_path=args.output,
            remote=args.remote
        )
    )
