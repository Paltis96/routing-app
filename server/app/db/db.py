from multiprocessing import pool
from fastapi import HTTPException, status

import asyncpg
import json


class AsyncDB():
    def __init__(
        self,
        dsn,
        codec='jsonb',
        min_size=1,
        max_size=10
    ) -> None:
        self.pool = None
        self.dsn = dsn
        self.codec = codec
        self.min_size = min_size
        self.max_size = max_size

    async def jsonb_codec(self, conn):
        await conn.set_type_codec(
            'jsonb',
            encoder=json.dumps,
            decoder=json.loads,
            schema='pg_catalog'
        )

    async def get_pool(self):
        if self.codec == 'jsonb':
            codec = self.jsonb_codec
        else:
            codec=None

        if not self.pool:
            self.pool = await asyncpg.create_pool(
                dsn=self.dsn,
                command_timeout=60,
                min_size=self.min_size,
                max_size=self.max_size,
                init=codec)
        return self.pool

    async def close_pool(self):
        await self.pool.close()

    async def connection(self):
        if not self.pool:
            await self.get_pool()
            
        async with self.pool.acquire() as db:
            yield db
