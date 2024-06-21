import pandas as pd
import jsonlines
import logging

from pathlib import Path
from tabulate import tabulate


Path('./out/data-insight').mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('./out/data-insight/insight.txt')
    ]
)

logger = logging.getLogger(__name__)


def print_section(title: str, printable) -> None:
    logger.info(
        '|| ' + title + '\n\n' +
        printable +
        '\n\n'
    )


def main():
    rows = []
    with jsonlines.open('./out/data-crawler/data.jsonl') as reader:
        for line in reader:
            line.pop('doc')
            rows.append(line)
    df = pd.DataFrame(columns=['ticker', 'title', 'document_type', 'year'], data=rows)

    logger.info(f'{" DATA INSIGHTS ":*^100}')

    # Print total number of documents
    print_section('Total number of collected documents:', '\t' + str(df.shape[0]))

    # Print available document types
    print_section('Collected document types:', '\t' + '\n\t'.join(set(df.document_type.T)))

    # Print amount of documents per document_type
    print_section(
        'Number of collected documents by document type:',
        tabulate(
            pd.DataFrame(df.groupby(['document_type']).size()),
            headers=['Document Type', 'Count'],
        )
    )

    # Print amount of documents per firm
    print_section(
        'Number of collected documents by firm:',
        tabulate(
            pd.DataFrame(df.groupby(['title']).size()),
            headers=['Firm', 'Count'],
        )
    )

    # Available documents by Stock
    print_section(
        'Stock documents available years',
        tabulate(
            df.groupby(['title', 'ticker', 'document_type'])
            .aggregate(lambda x: ','.join([str(y) for y in list(x)])).reset_index(),
            showindex=False,
            headers=['Firm', 'Ticker', 'Document Type', 'Years'],
            maxcolwidths=[None, None, None, 25]
        )
    )

    logger.info(f'{"":*^100}')


if __name__ == '__main__':
    main()
