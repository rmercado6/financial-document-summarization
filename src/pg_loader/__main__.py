from configparser import ConfigParser
from typing import Optional

import psycopg2
import jsonlines
import tiktoken


tiktoken_encoding = tiktoken.encoding_for_model('gpt-4o-mini-2024-07-18')


def load_config(filename='database.ini', section='postgresql'):
    parser = ConfigParser()
    parser.read(filename)

    # get section, default to postgresql
    config = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            config[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file'.format(section, filename))

    return config


def insert_document(document):
    """ Insert a new vendor into the vendors table """

    sql = """INSERT INTO documents(title, ticker, year, document_type, doc, tokens) VALUES(%s, %s, %s, %s, %s, %s);"""

    vendor_id = None
    config = load_config()

    try:
        with psycopg2.connect(**config) as conn:
            with conn.cursor() as cur:
                # execute the INSERT statement
                cur.execute(sql, document)

                # commit the changes to the database
                conn.commit()
    except (Exception, psycopg2.DatabaseError) as error:
        print(error)
        print(document[:4])
    finally:
        return vendor_id


def get_doc_size(document):
    return len(tiktoken_encoding.encode(document))


if __name__ == '__main__':
    file: Optional[tuple] = None
    with jsonlines.open('./data/documents.jsonl') as reader:
        for line in reader:
            line['tokens'] = get_doc_size(line['doc'])
            insert_document(tuple(line.values()))
