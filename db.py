import os
import asyncpg

pool = None

SCHEMA = '''
CREATE TABLE IF NOT EXISTS points_balance(
    user_id BIGINT PRIMARY KEY,
    balance INT DEFAULT 0,
    total_earned INT DEFAULT 0,
    total_spent INT DEFAULT 0
);
'''

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"]
    )
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)
    print("Database connected")

async def get_balance(user_id:int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance,total_earned FROM points_balance WHERE user_id=$1",
            user_id
        )
    if not row:
        return {"balance":0,"total_earned":0}
    return {
        "balance": row["balance"],
        "total_earned": row["total_earned"]
    }
