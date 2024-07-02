import tiktoken
import langchain
from spacy.lang.en import English

from src.summarization.document import Document


class TextSplitter:

    __DOC_MAX_TOKENS = 1000
    __TOLERANCE = 200

    def __init__(self):
        self.__nlp = English()
        self.__nlp.add_pipe("sentencizer")
        self.__encoding = tiktoken.encoding_for_model('text-embedding-ada-002')

    def chunk_document(self, document: Document):
        sentences, chunked_docs = [], []
        token_sum, str_sum = 0, ""
        docs = self.__nlp(document.content)

        for sentence in docs.sents:
            sent_total_tokens = len(self.__encoding.encode(sentence.text))
            if sent_total_tokens + token_sum >= self.__DOC_MAX_TOKENS + self.__TOLERANCE:
                sentences.append(str_sum)
                str_sum = sentence.text
                token_sum = sent_total_tokens
            else:
                str_sum += sentence.text
                token_sum += sent_total_tokens

        if str_sum:
            sentences.append(str_sum)

        for chunk in sentences:
            chunked_docs.append(langchain.schema.Document(page_content=chunk))

        return chunked_docs
