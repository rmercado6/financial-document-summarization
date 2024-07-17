import jsonlines

from fastapi import FastAPI

from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/documents")
def home():
    docs = []
    with jsonlines.open('./out/data-crawler/data.jsonl') as reader:
        for line in reader:
            # line['preview'] = line.pop('doc')[:100]
            line.pop('doc')
            docs.append(line)
    return docs


@app.get("/documents/{title}/{ticker}/{document_type}/{year}")
def document(title: str, ticker: str, document_type: str, year: str):
    doc = None
    with jsonlines.open('./out/data-crawler/data.jsonl') as reader:
        for line in reader:
            if line['title'] == title and line['ticker'] == ticker \
                    and line['document_type'] == document_type and year == str(line['year']):
                doc = line
                break
    return doc
