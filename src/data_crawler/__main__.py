import asyncio
import logging

from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table, scrape_hl_index_stock_pages
from src.data_crawler.constants import DATA_SRC_URLS, N_PAGES, LOGGER_NAME
from src.data_crawler.logger import safely_start_logger


logger: logging.Logger = logging.getLogger(LOGGER_NAME)


async def main():
    await safely_start_logger()     # initialize the logger

    logger.info(f'starting')

    # Get stocks list from HL Stocks Table
    stocks = await scrape_hl_index_stocks_table(
        DATA_SRC_URLS['hl-base'] + DATA_SRC_URLS['hl-ftse-all-share-index'],
        N_PAGES
    )

    first_stock = list(stocks.keys())[0]

    # Scrape HL financial reports
    scraped_data = await scrape_hl_index_stock_pages({first_stock: stocks[first_stock]})

    logger.info(f'DONE')


if __name__ == '__main__':
    asyncio.run(main())
