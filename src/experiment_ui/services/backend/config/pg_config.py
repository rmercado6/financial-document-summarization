import os
import asyncpg

from logging import getLogger

logger = getLogger("uvicorn")

PG_CONNECTION_CONFIG = {
    "user": os.getenv("PG_USERNAME"),
    "password": os.getenv("PG_PASSWORD"),
    "host": os.getenv("PG_HOSTNAME"),
    "dbname": os.getenv("PG_DB_NAME"),
    "port": os.getenv("PG_PORT"),
}


class Database:
    def __init__(
            self,
            user=PG_CONNECTION_CONFIG["user"],
            password=PG_CONNECTION_CONFIG["password"],
            host=PG_CONNECTION_CONFIG["host"],
            dbname=PG_CONNECTION_CONFIG["dbname"],
            port=PG_CONNECTION_CONFIG["port"],
    ):
        self.user = user
        self.password = password
        self.host = host
        self.port = port
        self.database = dbname
        self._cursor = None

        self._connection_pool = None

    async def connect(self):
        if not self._connection_pool:
            try:
                self._connection_pool = await asyncpg.create_pool(
                    min_size=1,
                    max_size=20,
                    command_timeout=60,
                    host=self.host,
                    port=self.port,
                    user=self.user,
                    password=self.password,
                    database=self.database,
                )
                logger.info("Database pool connection opened.")

            except Exception as e:
                logger.exception(e)

    async def fetch_rows(self, query: str, *args):
        if not self._connection_pool:
            await self.connect()
        else:
            con = await self._connection_pool.acquire()
            try:
                result = await con.fetch(query, *args)
                return result
            except Exception as e:
                logger.exception(e)
            finally:
                await self._connection_pool.release(con)

    async def close(self):
        if not self._connection_pool:
            try:
                await self._connection_pool.close()
                logger.info("Database pool connection closed.")
            except Exception as e:
                logger.exception(e)
