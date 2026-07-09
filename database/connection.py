import os
import asyncpg

pool=None
async def connect():
    global pool
    pool=await asyncpg.create_pool(os.getenv('DATABASE_URL'))
    print('Database Connected')
