import pandas as pd
import logging
import matplotlib.pyplot as plt
import seaborn as sns

from pathlib import Path
from tabulate import tabulate

from src.pg_loader import execute_fetch_query

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


def get_stats(df: pd.DataFrame):
    logger.info(f'{" DATA INSIGHTS ":*^90}')

    # plot distribution of document size by document_type
    sns.displot(
        df, x="tokens", col="document_type",
        facet_kws=dict(margin_titles=True, sharey=False),
        log_scale=(True, False), col_wrap=2, bins=10, kde=True
    )
    plt.savefig('./out/data-insight/document_size_dist.png')

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

    # Print amount of documents per document_type
    print_section(
        'Document file size statistics for all collected data:',
        tabulate(
            df.aggregate({'tokens': ['min', 'max', 'mean', 'median', 'std', 'var']}).T,
            showindex=False,
            headers=['Min', 'Max', 'Mean', 'Median', 'Standard Deviation', 'Variance'],
        )
    )

    # Print amount of documents per document_type
    print_section(
        'Document file size statistics by document type:',
        tabulate(
            df.groupby(['document_type']).aggregate({'tokens': ['min', 'max', 'mean', 'median', 'std', 'var']}),
            headers=['Document Type', 'Min', 'Max', 'Mean', 'Median', 'Standard Deviation', 'Variance'],
        )
    )
    df.drop(columns=['tokens'], inplace=True)

    # Print number of documents per firm stats
    documents_per_firm = pd.DataFrame(df.groupby(['ticker']).size(), columns=['documents'])
    sns.displot(documents_per_firm, x='documents', kde=True)
    plt.savefig('./out/data-insight/documents_per_firm.png')
    print_section(
        'Collected documents by firm:',
        tabulate(
            documents_per_firm.aggregate({'documents': ['min', 'max', 'mean', 'median', 'std', 'var']}).T,
            showindex=False,
            headers=['Min', 'Max', 'Mean', 'Median', 'Standard Deviation', 'Variance'],
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

    logger.info(f'{"":*^90}')


def load_data():
    query = """
    SELECT upper(title), ticker, document_type, year, tokens 
    FROM documents
    """
    rows = execute_fetch_query(query, ())
    df = pd.DataFrame(
        columns=['title', 'ticker', 'document_type', 'year', 'tokens'],
        data=rows
    )

    return df


if __name__ == '__main__':
    get_stats(load_data())
