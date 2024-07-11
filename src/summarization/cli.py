import argparse

from src.summarization.constants import MODELS, PIPELINES, DEFAULT_MODEL, DEFAULT_PIPELINE


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '--model',
        type=str,
        help='The name of the model to use',
        default=DEFAULT_MODEL,
        choices=MODELS
    )
    parser.add_argument(
        '--pipeline',
        type=str,
        help='The summarization pipeline to use',
        default=DEFAULT_PIPELINE,
        choices=PIPELINES
    )
    return parser.parse_args()
