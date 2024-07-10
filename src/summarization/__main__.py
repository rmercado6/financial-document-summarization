import logging

import jsonlines

from load_dotenv import load_dotenv
from langchain_text_splitters.markdown import MarkdownTextSplitter

from src.summarization.models import load_model
from src.summarization.document import Document
from src.summarization.pipelines import refine, map_reduce
from src.summarization.constants import CHUNK_SIZE, CHUNK_OVERLAP, MODELS, PIPELINES
from src.summarization.cli import get_args


logging.basicConfig(
    format='{asctime} - [{levelname:.3}]: {name:>12.12} | {filename:>15.15} [{lineno:4}] | {message}',
    style='{',
    level=logging.INFO,
    handlers=[logging.StreamHandler()]
)
logging.getLogger().setLevel(logging.INFO)

# Load the .env file
env_found = load_dotenv(".env")
if not env_found:
    logging.warning("The .env file is not found. Please ensure environment variables are set properly.")


if __name__ == "__main__":
    logging.info(f'{" SUMMARIZE ":-^100}')
    args = get_args()

    # Loading the model
    model = load_model(args.model)
    logging.info(f'Loaded model: {args.model}')

    # Load first document in dataset
    doc: Document or None = None
    with jsonlines.open('./out/pdf_converter/file.jsonl') as f:
        for line in f:
            if line['document_type'] != 'annual_report':
                continue
            doc = Document(line)
            logging.info(f'Loaded document: {line["title"]} {line["document_type"]} {line["year"]}')
            break

    if not doc:
        logging.error('No Document found on datasource.')
        exit()

    # Chunk text
    text_splitter = MarkdownTextSplitter(chunk_size=CHUNK_SIZE[args.model], chunk_overlap=CHUNK_OVERLAP[args.model])
    chunks = doc.get_chunks(text_splitter)

    # Validate known pipeline
    if args.pipeline not in PIPELINES:
        logging.error(f'Unknown pipeline "{args.pipeline}".')
        exit()

    # Do summarize pipeline
    pipeline_outputs = None
    if args.pipeline == 'refine':
        pipeline_outputs = refine(model, chunks, True)
    elif args.pipeline == 'mapreduce':
        pipeline_outputs = map_reduce(model, chunks, True)

    # Log outputs
    if not pipeline_outputs:
        logging.error(f'Summarization request returned no response.')
        exit()

    # Print intermediate steps
    for k, v in pipeline_outputs.items():
        logging.info(f'{v}')

    # Print final output
    print(pipeline_outputs['output_text'])
