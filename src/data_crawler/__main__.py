import asyncio
import logging

from src.data_crawler.logger import safely_start_logger
from src.data_crawler.constants import DATA_SRC_URLS, N_PAGES, LOGGER_NAME
from src.data_crawler.hl_scrape import scrape_hl_index_stocks_table
from src.data_crawler.ar_scrape import scrape_ar_stocks_table
from src.data_crawler.scrape_requests.handlers import scrape_request_handler


logger: logging.Logger = logging.getLogger(LOGGER_NAME)


async def main():
    await safely_start_logger()     # initialize the logger

    logger.info(f'starting')

    # Get stocks list from HL Stocks Table
    hr_scrape_requests = await scrape_hl_index_stocks_table(
        DATA_SRC_URLS['hl-base'] + DATA_SRC_URLS['hl-ftse-all-share-index'],
        N_PAGES
    )

    # Get stocks list from AR Stocks Table
    ar_scrape_requests = scrape_ar_stocks_table(DATA_SRC_URLS['ar-base'] + DATA_SRC_URLS['ar-ftse-all-share-index'])

    scrape_requests = hr_scrape_requests + ar_scrape_requests

    # limited_requests = scrape_requests[:10]

    # Start the scraping process
    await scrape_request_handler(scrape_requests)

    logger.info('DONE')


if __name__ == '__main__':
    asyncio.run(main())
