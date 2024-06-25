class Document:

    __title: str
    __ticker: str
    __year: str
    __type: str
    __content: str

    def __init__(
            self,
            jsonlines: dict = None,
            title: str = None,
            ticker: str = None,
            year: str = None,
            type: str = None,
            content: str = None
    ):
        if jsonlines is not None:
            self.__title = jsonlines['title']
            self.__ticker = jsonlines['ticker']
            self.__year = jsonlines['year']
            self.__type = jsonlines['document_type']
            self.__content = jsonlines['doc']
        else:
            self.__title = title
            self.__year = year
            self.__ticker = ticker
            self.__type = type
            self.__content = content

    def get_chunks(self) -> list[str]:
        pass

    @property
    def title(self) -> str:
        return self.__title

    @property
    def ticker(self) -> str:
        return self.__ticker

    @property
    def year(self) -> str:
        return self.__year

    @property
    def type(self) -> str:
        return self.__type

    @property
    def content(self) -> str:
        return self.__content
