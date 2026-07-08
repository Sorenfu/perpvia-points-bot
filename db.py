import os
import asyncpg

pool = None

SCHEMA = """
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
    reason_code TEXT NOT NULL,
    detail TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS daily_checkin(
    user_id BIGINT PRIMARY KEY,
    last_checkin DATE,
    streak INT DEFAULT 0
);
"""


async def init_pool():
    global pool
    pool = await asyncpg.create_pool(
        dsn=os.environ["DATABASE_URL"]
    )

    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)

    print("Database connected")
