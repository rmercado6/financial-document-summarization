import argparse

import jsonlines

from src.summarization.models import load_model
from src.summarization.document import Document
from src.summarization.text_splitter import TextSplitter
from src.summarization.refine import refine
from src.summarization.mapreduce import map_reduce


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Process a PDF file with a specified model.')
    parser.add_argument('-m', '--model', type=str, help='The name of the model to use', default='llama')
    args = parser.parse_args()

    # Loading the model
    model = load_model(args.model)

    # Load first document in dataset
    doc: Document
    with jsonlines.open('./out/data-crawler/data.jsonl') as f:
        for line in f:
            doc = Document(line)
            break

    # Chunk text
    text_splitter = TextSplitter()
    doc.chunks = text_splitter.chunk_document(doc)

    # Do refine pipeline
    refine_outputs = refine(model, doc.chunks, True)
    # map_reduce_outputs = map_reduce(model, doc.chunks, True)

    # Print intermediate steps
    for k, v in refine_outputs.items():
        print(v)

    # Print final output
    print(refine_outputs['output_text'])
