import jsonlines
import logging
import os
import time

from pathlib import Path
from datetime import datetime
from uuid import uuid4

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from langchain_text_splitters.markdown import MarkdownTextSplitter

from src.experiment_ui.services.backend.config.pg_config import Database

from src.summarization.models import load_model
from src.summarization.document import Document
from src.summarization.pipelines import refine, map_reduce
from src.summarization.constants import CHUNK_SIZE, CHUNK_OVERLAP, PIPELINES

BOOLEAN_TRUE_VALUES = (1, 1.0, '1', '1.0', 'true', 'yes', 'y', 'on')
DATA_PATH = './data/'
RESPONSES_FILE = 'experiment_responses.jsonl'
COMMENTS_FILE = 'experiment_comments.jsonl'
DOCUMENTS_FILE = 'documents.jsonl'

Path(DATA_PATH).mkdir(parents=True, exist_ok=True)
Path(DATA_PATH + RESPONSES_FILE).touch()
Path(DATA_PATH + COMMENTS_FILE).touch()
Path(DATA_PATH + DOCUMENTS_FILE).touch()

MOCK_MODE = os.environ['MOCK_QUERY_RESPONSE'].lower()
MOCK_RESPONSE = None
try:
    with jsonlines.open(DATA_PATH + RESPONSES_FILE) as reader:
        for line in reader:
            MOCK_RESPONSE = line
            break
except FileNotFoundError:
    MOCK_RESPONSE = None

if 'MOCK_QUERY_RESPONSE_SLEEP' in os.environ:
    MOCK_SLEEP = int(os.environ['MOCK_QUERY_RESPONSE_SLEEP'])
else:
    MOCK_SLEEP = 5

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('uvicorn')

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    database_instance = Database()
    await database_instance.connect()
    app.state.db = database_instance
    logger.info("Server Startup")


@app.on_event("shutdown")
async def shutdown_event():
    if not app.state.db:
        await app.state.db.close()
    logger.info("Server Shutdown")


async def load_document_from_dataset(request: Request, title: str, ticker: str, document_type: str, year: str) -> dict:
    doc = await request.app.state.db.fetch_rows(f"""
        SELECT * from documents
        WHERE title = '{title}' AND ticker = '{ticker}' AND document_type = '{document_type}' AND year = '{year}';
        """)
    return doc[0]


async def load_document_from_dataset_by_uuid(request: Request, uuid: str) -> dict:
    doc = await request.app.state.db.fetch_rows(f"SELECT * from documents WHERE document_id = '{uuid}';")
    return doc[0]


def load_experiment_from_file(uuid: str) -> dict:
    exp = None
    with jsonlines.open(DATA_PATH + RESPONSES_FILE) as r:
        for _ in r:
            if _['uuid'] == uuid:
                exp = _
                break
    return exp


@app.get("/documents")
async def documents(request: Request):
    docs = await request.app.state.db.fetch_rows("""
    SELECT document_id, title, ticker, document_type, year, tokens, src_url from documents;
    """)
    docs.sort(key=lambda x: x['title'].lower())
    return docs


@app.get("/experiments")
def experiments():
    experiments = []
    with jsonlines.open(DATA_PATH + RESPONSES_FILE) as r:
        for _ in r:
            # line['preview'] = line.pop('doc')[:100]
            _.pop('pipeline_outputs')
            experiments.append(_)
    return experiments


@app.get("/comments/{document_uuid}")
def comments(document_uuid: str):
    comments_list = []
    with jsonlines.open(DATA_PATH + COMMENTS_FILE) as r:
        for _ in r:
            logger.info(_)
            if _['document_uuid'] == document_uuid:
                comments_list.append(_)
    comments_list.sort(key=lambda x: x['datetime'], reverse=True)
    return comments_list


@app.get("/documents/{title}/{ticker}/{document_type}/{year}")
async def document(request: Request, title: str, ticker: str, document_type: str, year: str):
    doc = await load_document_from_dataset(request, title, ticker, document_type, year)
    if not doc:
        raise HTTPException(404, 'Document not found.')
    return doc


@app.get("/documents/{uuid}")
async def document(request: Request, uuid: str):
    doc = await load_document_from_dataset_by_uuid(request, uuid)
    if not doc:
        raise HTTPException(404, 'Document not found.')
    return doc


@app.get("/experiments/{uuid}")
async def experiment(request: Request, uuid: str):
    exp = load_experiment_from_file(uuid)
    if not exp:
        raise HTTPException(404, f'Experiment with UUID {uuid} not found.')
    d = await load_document_from_dataset_by_uuid(request, exp['query']['document'])
    exp["original_document"] = d
    return exp


@app.post("/query_model")
async def query_model(request: Request, body: dict):
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
    d = await load_document_from_dataset_by_uuid(request, body['document'])
    if not d:
        raise HTTPException(status_code=404, detail=f'Document not found.')
    doc: Document = Document(d)
    logger.debug(
        f"Loaded document {d['title']} {d['document_type']} {d['year']}")

    # Chunk text
    text_splitter = MarkdownTextSplitter(
        chunk_size=CHUNK_SIZE[body['model']],
        chunk_overlap=CHUNK_OVERLAP[body['model']]
    )
    chunks = doc.get_chunks(text_splitter)
    logger.debug(f"Document has been split into {len(chunks)} chunks")

    # Do summarize pipeline
    logger.info(f"Querying pipeline {body['pipeline']}")
    start_time = time.time()
    pipeline_outputs = None
    if body['pipeline'] == 'refine':
        pipeline_outputs = refine(
            model,
            chunks,
            True,
            initial_prompt=body['prompt_1'],
            refine_prompt=body['prompt_2'],
            similarity_filter=body['similarity_filter'],
            task=body['task'],
        )
    elif body['pipeline'] == 'mapreduce':
        pipeline_outputs = map_reduce(model, chunks, True, map_prompt=body['prompt_1'], combine_prompt=body['prompt_2'])

    # Log outputs
    if not pipeline_outputs:
        raise HTTPException(status_code=503, detail="Summarization request returned no response.")

    logger.debug(f"Got response.")

    response: dict = {
        'uuid': uuid4(),
        'execution_time': start_time - time.time(),
        'time': datetime.now(),
        'query': body,
        'pipeline_outputs': pipeline_outputs
    }

    # write output to file
    with jsonlines.open(DATA_PATH + RESPONSES_FILE, 'a') as writer:
        writer.write(jsonable_encoder(response))

    response['original_document'] = d

    # set mock response if there was none
    if MOCK_MODE in BOOLEAN_TRUE_VALUES and not MOCK_RESPONSE:
        MOCK_RESPONSE = response

    # Return final output
    return response


@app.post("/comment")
def post_comment(body: dict):
    comment = {
        'document_uuid': body['document_uuid'],
        'datetime': datetime.now(),
        'text': body['text'],
    }
    with jsonlines.open(DATA_PATH + COMMENTS_FILE, 'a') as _:
        _.write(jsonable_encoder(comment))
    return comment
