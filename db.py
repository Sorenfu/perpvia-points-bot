import os,asyncpg
pool=None
async def init_pool():
 global pool
 pool=await asyncpg.create_pool(dsn=os.environ['DATABASE_URL'])
