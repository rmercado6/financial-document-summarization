import jsonlines
import logging
import os
import time

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from langchain_text_splitters.markdown import MarkdownTextSplitter

from src.summarization.models import load_model
from src.summarization.document import Document
from src.summarization.pipelines import refine, map_reduce
from src.summarization.constants import CHUNK_SIZE, CHUNK_OVERLAP, PIPELINES


BOOLEAN_TRUE_VALUES = (1, 1.0, '1', '1.0', 'true', 'yes', 'y', 'on')

MOCK_MODE = os.environ['MOCK_QUERY_RESPONSE'].lower()
MOCK_RESPONSE = None
try:
    with jsonlines.open('./out/experiment_ui/responses.jsonl') as reader:
        for line in reader:
            MOCK_RESPONSE = line
            break
except FileNotFoundError:
    MOCK_RESPONSE = None

if 'MOCK_QUERY_RESPONSE_SLEEP' in os.environ:
    MOCK_SLEEP = int(os.environ['MOCK_QUERY_RESPONSE_SLEEP'])
else:
    MOCK_SLEEP = 5

logger = logging.getLogger('uvicorn.error')
logger.setLevel(logging.INFO)

Path('./out/experiment_ui').mkdir(parents=True, exist_ok=True)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


def load_document_from_dataset(title: str, ticker: str, document_type: str, year: str) -> dict:
    doc = None
    with jsonlines.open('./out/data-crawler/data.jsonl') as reader:
        for line in reader:
            if line['title'] == title and line['ticker'] == ticker \
                    and line['document_type'] == document_type and year == str(line['year']):
                doc = line
                break
    return doc


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
    return load_document_from_dataset(title, ticker, document_type, year)


@app.post("/query_model")
def query_model(body: dict):
    global MOCK_RESPONSE
    # Return mock if mock mode is True
    if MOCK_MODE in BOOLEAN_TRUE_VALUES and MOCK_RESPONSE:
        time.sleep(MOCK_SLEEP)
        return MOCK_RESPONSE

    # Validate known pipeline
    if body['pipeline'] not in PIPELINES:
        raise HTTPException(status_code=400, detail=f'Bad request. Unknown Pipeline {body["pipeline"]}')

    # Loading the model
    try:
        model = load_model(body['model'])
        logger.debug(f'Loaded model {body["model"]}')
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Load document from dataset
    doc: Document = Document(
        load_document_from_dataset(
            body['document']['title'],
            body['document']['ticker'],
            body['document']['document_type'],
            body['document']['year']
        )
    )
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    logger.debug(
        f"Loaded document {body['document']['title']} {body['document']['document_type']} {body['document']['year']}")

    # Chunk text
    text_splitter = MarkdownTextSplitter(
        chunk_size=CHUNK_SIZE[body['model']],
        chunk_overlap=CHUNK_OVERLAP[body['model']]
    )
    chunks = doc.get_chunks(text_splitter)
    logger.debug(f"Document has been split into {len(chunks)} chunks")

    # Do summarize pipeline
    logger.info(f"Querying pipeline {body['pipeline']}")
    pipeline_outputs = None
    if body['pipeline'] == 'refine':
        pipeline_outputs = refine(model, chunks, True)
    elif body['pipeline'] == 'mapreduce':
        pipeline_outputs = map_reduce(model, chunks, True)

    # Log outputs
    if not pipeline_outputs:
        raise HTTPException(status_code=503, detail="Summarization request returned no response.")

    logger.debug(f"Got response.")

    response: dict = {
        'uuid': uuid4(),
        'time': datetime.now(),
        'query': body,
        'pipeline_outputs': pipeline_outputs
    }

    # write output to file
    with jsonlines.open('./out/experiment_ui/responses.jsonl', 'a') as writer:
        writer.write(jsonable_encoder(response))

    if MOCK_MODE in BOOLEAN_TRUE_VALUES and not MOCK_RESPONSE:
        MOCK_RESPONSE = response

    # Return final output
    return response
