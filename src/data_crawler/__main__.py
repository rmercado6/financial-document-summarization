import asyncio

from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.constants import DATA_SRC_URLS, N_PAGES


if __name__ == '__main__':
    stocks = asyncio.run(
        scrape_hl_index_stocks_table(DATA_SRC_URLS['hl-base'] + DATA_SRC_URLS['hl-ftse-all-share-index'], N_PAGES)
    )
    first_stock = list(stocks.keys())[0]
    scraped_data = asyncio.run(scrape_hl_index_stock_pages({first_stock: stocks[first_stock]}))
    print('Done')


