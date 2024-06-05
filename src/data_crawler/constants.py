import httpx


N_PAGES = 6

DATA_SRC_URLS = {
    'hl-base': 'https://www.hl.co.uk',
    'hl-ftse-all=share-index': '/shares/stock-market-summary/ftse-all-share',
    'hl-financial-statement-and-reports': '/financial-statements-and-reports'
}

HTTP_CLIENT_CONFIG = {
    "limits": httpx.Limits(max_connections=10),
    "timeout": httpx.Timeout(60.0),
    "headers": {
        "Accept-Language": "en-US,en;q=0.9",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/96.0.4664.110 Safari/537.36",
    }
}
