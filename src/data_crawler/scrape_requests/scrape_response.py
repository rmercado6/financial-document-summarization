from .scrape_request import ScrapeRequest


class ScrapeResponse:
    """ConsumerResponse class
    Wrapper for the scraping responses.
    """
    __metadata: dict
    __data: str or bytes
    __further_requests: list[ScrapeRequest] or None

    def __init__(self, metadata: dict, data: str or bytes, further_requests: list[ScrapeRequest] = None) -> None:
        self.__metadata = metadata.copy()
        if 'method' not in self.__metadata:
            self.__metadata['method'] = 'GET'
        self.__data = data
        self.__further_requests = further_requests

    @property
    def metadata(self) -> dict:
        """metadata: dict"""
        return self.__metadata

    @property
    def data(self) -> str or bytes:
        """data: any
        The scraped data.
        """
        return self.__data

    @property
    def further_requests(self) -> list[ScrapeRequest]:
        """further_requests: list[ScrapeRequest]
        List of requests to further scrape, if any were generated during the scraping process.
        """
        return self.__further_requests

    def jsonl(self) -> dict:
        return {
            'title': self.metadata['share']['title'],
            'ticker': self.metadata['share']['ticker'],
            'year': self.metadata['year'] if 'year' in self.metadata.keys() else None,
            'document_type': self.metadata['data_type'],
            'doc': self.data if type(self.data) is str else self.data.decode('utf-8'),
        }
