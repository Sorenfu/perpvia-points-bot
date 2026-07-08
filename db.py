# Phase 2 database upgrade
# Added points ledger and balance management interfaces
import os
import asyncpg

pool = None

SCHEMA = '''
CREATE TABLE IF NOT EXISTS points_balance(
    user_id BIGINT PRIMARY KEY,
    balance INT NOT NULL DEFAULT 0,
    total_earned INT NOT NULL DEFAULT 0,
    total_spent INT NOT NULL DEFAULT 0,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS points_ledger(
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL,
    change_amount INT NOT NULL,
    reason_code VARCHAR(64) NOT NULL,
    detail TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
'''

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(dsn=os.environ["DATABASE_URL"])
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)
    print("Database connected")

async def get_balance(user_id:int):
    async with pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT balance,total_earned,total_spent FROM points_balance WHERE user_id=$1",
            user_id
        )
    if not row:
        return {"balance":0,"total_earned":0,"total_spent":0}
    return dict(row)
