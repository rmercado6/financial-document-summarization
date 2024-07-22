import argparse


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        'path',
        type=str,
        help='path of the file to be converted.'
    )
    parser.add_argument(
        'title',
        type=str,
        help='title of the company to whom the file refers to.'
    )
    parser.add_argument(
        'ticker',
        type=str,
        help='ticker of the company to whom the file refers to.',
        default=''
    )
    parser.add_argument(
        'document_type',
        type=str,
        help='document type of the file to be converted.'
    )
    parser.add_argument(
        'year',
        type=str,
        help='year in which the document was published or to which it refers to.'
    )
    parser.add_argument(
        '--output',
        type=str,
        help='The output path in where to place the output data.jsonl file.',
        default='./data'
    )
    parser.add_argument(
        '-r',
        '--remote',
        action='store_true',
        help='Whether or not the path belongs to a remote file url.',
    )
    return parser.parse_args()
