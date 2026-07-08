# ============================================================
# db.py - PostgreSQL 连接、建表、积分/商城核心事务
# ============================================================

from __future__ import annotations

import os
from datetime import date, datetime, timedelta, timezone
from typing import Any

import asyncpg

pool: asyncpg.Pool | None = None

SCHEMA = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT PRIMARY KEY,
    username TEXT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS points_balance (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    balance INT NOT NULL DEFAULT 0 CHECK (balance >= 0),
    total_earned INT NOT NULL DEFAULT 0 CHECK (total_earned >= 0),
    total_spent INT NOT NULL DEFAULT 0 CHECK (total_spent >= 0),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS points_ledger (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    change INT NOT NULL,
    balance_after INT NOT NULL,
    reason_code VARCHAR(64) NOT NULL,
    detail TEXT,
    operator_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_points_ledger_user_time ON points_ledger(user_id, created_at DESC);

CREATE TABLE IF NOT EXISTS role_grant_log (
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    role_id BIGINT NOT NULL,
    rule_id VARCHAR(64) NOT NULL,
    points INT NOT NULL,
    granted_at TIMESTAMPTZ DEFAULT now(),
    PRIMARY KEY (user_id, role_id)
);

CREATE TABLE IF NOT EXISTS daily_checkins (
    user_id BIGINT PRIMARY KEY REFERENCES users(user_id) ON DELETE CASCADE,
    last_checkin DATE NOT NULL,
    streak INT NOT NULL DEFAULT 1,
    total_checkins INT NOT NULL DEFAULT 1,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS redeem_products (
    id BIGSERIAL PRIMARY KEY,
    code VARCHAR(64) UNIQUE NOT NULL,
    name TEXT NOT NULL,
    description TEXT DEFAULT '',
    price INT NOT NULL CHECK (price > 0),
    stock INT NOT NULL DEFAULT 0 CHECK (stock >= 0),
    active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE TABLE IF NOT EXISTS redeem_orders (
    id BIGSERIAL PRIMARY KEY,
    user_id BIGINT NOT NULL REFERENCES users(user_id) ON DELETE CASCADE,
    product_id BIGINT NOT NULL REFERENCES redeem_products(id),
    product_code VARCHAR(64) NOT NULL,
    product_name TEXT NOT NULL,
    price INT NOT NULL,
    status VARCHAR(32) NOT NULL DEFAULT 'pending',
    note TEXT DEFAULT '',
    operator_id BIGINT,
    created_at TIMESTAMPTZ DEFAULT now(),
    updated_at TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX IF NOT EXISTS idx_redeem_orders_user_time ON redeem_orders(user_id, created_at DESC);
CREATE INDEX IF NOT EXISTS idx_redeem_orders_status_time ON redeem_orders(status, created_at DESC);

CREATE TABLE IF NOT EXISTS admin_logs (
    id BIGSERIAL PRIMARY KEY,
    operator_id BIGINT NOT NULL,
    action VARCHAR(64) NOT NULL,
    target_user_id BIGINT,
    detail TEXT,
    created_at TIMESTAMPTZ DEFAULT now()
);
"""


def _require_pool() -> asyncpg.Pool:
    if pool is None:
        raise RuntimeError("Database pool is not initialized")
    return pool


async def init_pool() -> None:
    global pool
    db_url = os.environ["DATABASE_URL"]
    pool = await asyncpg.create_pool(dsn=db_url, min_size=1, max_size=5)
    async with pool.acquire() as conn:
        await conn.execute(SCHEMA)
    print("Database connected and schema is ready")


async def close_pool() -> None:
    global pool
    if pool is not None:
        await pool.close()
        pool = None


async def ensure_user(user_id: int, username: str | None = None) -> None:
    p = _require_pool()
    await p.execute(
        """
        INSERT INTO users(user_id, username) VALUES($1, $2)
        ON CONFLICT(user_id) DO UPDATE SET
            username = COALESCE($2, users.username),
            updated_at = now()
        """,
        user_id,
        username,
    )
    await p.execute(
        """
        INSERT INTO points_balance(user_id, balance, total_earned, total_spent)
        VALUES($1, 0, 0, 0)
        ON CONFLICT(user_id) DO NOTHING
        """,
        user_id,
    )


async def change_points(
    user_id: int,
    amount: int,
    reason_code: str,
    detail: str = "",
    operator_id: int | None = None,
    username: str | None = None,
) -> dict[str, Any]:
    """统一积分入口。正数加分，负数扣分。扣分时严格防止余额为负。"""
    if amount == 0:
        raise ValueError("amount cannot be zero")

    p = _require_pool()
    async with p.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO users(user_id, username) VALUES($1, $2)
                ON CONFLICT(user_id) DO UPDATE SET
                    username = COALESCE($2, users.username),
                    updated_at = now()
                """,
                user_id,
                username,
            )
            await conn.execute(
                """
                INSERT INTO points_balance(user_id, balance, total_earned, total_spent)
                VALUES($1, 0, 0, 0)
                ON CONFLICT(user_id) DO NOTHING
                """,
                user_id,
            )

            if amount < 0:
                row = await conn.fetchrow(
                    """
                    UPDATE points_balance
                    SET balance = balance + $2,
                        total_spent = total_spent + ABS($2),
                        updated_at = now()
                    WHERE user_id = $1 AND balance >= ABS($2)
                    RETURNING balance, total_earned, total_spent
                    """,
                    user_id,
                    amount,
                )
                if row is None:
                    current = await conn.fetchval("SELECT balance FROM points_balance WHERE user_id=$1", user_id)
                    raise ValueError(f"insufficient_balance:{current or 0}")
            else:
                row = await conn.fetchrow(
                    """
                    UPDATE points_balance
                    SET balance = balance + $2,
                        total_earned = total_earned + $2,
                        updated_at = now()
                    WHERE user_id = $1
                    RETURNING balance, total_earned, total_spent
                    """,
                    user_id,
                    amount,
                )

            ledger = await conn.fetchrow(
                """
                INSERT INTO points_ledger(user_id, change, balance_after, reason_code, detail, operator_id)
                VALUES($1, $2, $3, $4, $5, $6)
                RETURNING id, created_at
                """,
                user_id,
                amount,
                row["balance"],
                reason_code,
                detail,
                operator_id,
            )
            return {
                "balance": row["balance"],
                "total_earned": row["total_earned"],
                "total_spent": row["total_spent"],
                "ledger_id": ledger["id"],
                "created_at": ledger["created_at"],
            }


async def get_balance(user_id: int, username: str | None = None) -> dict[str, int]:
    await ensure_user(user_id, username)
    p = _require_pool()
    row = await p.fetchrow(
        "SELECT balance, total_earned, total_spent FROM points_balance WHERE user_id=$1",
        user_id,
    )
    return {
        "balance": row["balance"],
        "total_earned": row["total_earned"],
        "total_spent": row["total_spent"],
    }


async def get_ledger(user_id: int, limit: int = 10) -> list[asyncpg.Record]:
    p = _require_pool()
    return await p.fetch(
        """
        SELECT change, balance_after, reason_code, detail, created_at
        FROM points_ledger
        WHERE user_id=$1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        user_id,
        limit,
    )


async def get_leaderboard(limit: int = 10) -> list[asyncpg.Record]:
    p = _require_pool()
    return await p.fetch(
        """
        SELECT b.user_id, COALESCE(u.username, '') AS username, b.balance, b.total_earned
        FROM points_balance b
        LEFT JOIN users u ON u.user_id = b.user_id
        ORDER BY b.balance DESC, b.total_earned DESC
        LIMIT $1
        """,
        limit,
    )


async def grant_role_points_once(
    user_id: int,
    username: str,
    role_id: int,
    points: int,
    rule_id: str,
    role_name: str,
) -> bool:
    p = _require_pool()
    async with p.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO users(user_id, username) VALUES($1, $2)
                ON CONFLICT(user_id) DO UPDATE SET username=$2, updated_at=now()
                """,
                user_id,
                username,
            )
            await conn.execute(
                "INSERT INTO points_balance(user_id) VALUES($1) ON CONFLICT DO NOTHING",
                user_id,
            )
            inserted = await conn.fetchrow(
                """
                INSERT INTO role_grant_log(user_id, role_id, rule_id, points)
                VALUES($1, $2, $3, $4)
                ON CONFLICT DO NOTHING
                RETURNING user_id
                """,
                user_id,
                role_id,
                rule_id,
                points,
            )
            if inserted is None:
                return False

    await change_points(user_id, points, rule_id, f"role:{role_id}:{role_name}", username=username)
    return True


async def checkin_daily(user_id: int, username: str, base_points: int, bonus_days: int, bonus_points: int) -> dict[str, Any]:
    today = datetime.now(timezone.utc).date()
    p = _require_pool()
    async with p.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO users(user_id, username) VALUES($1, $2)
                ON CONFLICT(user_id) DO UPDATE SET username=$2, updated_at=now()
                """,
                user_id,
                username,
            )
            row = await conn.fetchrow(
                "SELECT last_checkin, streak, total_checkins FROM daily_checkins WHERE user_id=$1 FOR UPDATE",
                user_id,
            )
            if row and row["last_checkin"] == today:
                return {"already": True, "streak": row["streak"], "points": 0}

            if row and row["last_checkin"] == today - timedelta(days=1):
                streak = row["streak"] + 1
            else:
                streak = 1

            earned = base_points
            bonus = 0
            if bonus_days > 0 and streak % bonus_days == 0:
                bonus = bonus_points
                earned += bonus

            await conn.execute(
                """
                INSERT INTO daily_checkins(user_id, last_checkin, streak, total_checkins)
                VALUES($1, $2, $3, 1)
                ON CONFLICT(user_id) DO UPDATE SET
                    last_checkin=$2,
                    streak=$3,
                    total_checkins=daily_checkins.total_checkins + 1,
                    updated_at=now()
                """,
                user_id,
                today,
                streak,
            )

    point_result = await change_points(user_id, earned, "DAILY_CHECKIN", f"streak:{streak};bonus:{bonus}", username=username)
    return {"already": False, "streak": streak, "points": earned, "bonus": bonus, "balance": point_result["balance"]}


async def upsert_product(code: str, name: str, description: str, price: int, stock: int, active: bool = True) -> None:
    p = _require_pool()
    await p.execute(
        """
        INSERT INTO redeem_products(code, name, description, price, stock, active)
        VALUES($1, $2, $3, $4, $5, $6)
        ON CONFLICT(code) DO UPDATE SET
            name=$2,
            description=$3,
            price=$4,
            stock=$5,
            active=$6,
            updated_at=now()
        """,
        code,
        name,
        description,
        price,
        stock,
        active,
    )


async def seed_products(products: list[dict[str, Any]]) -> None:
    for item in products:
        await upsert_product(
            item["code"],
            item["name"],
            item.get("description", ""),
            int(item["price"]),
            int(item.get("stock", 0)),
            bool(item.get("active", True)),
        )


async def list_products(active_only: bool = True) -> list[asyncpg.Record]:
    p = _require_pool()
    if active_only:
        return await p.fetch(
            "SELECT id, code, name, description, price, stock, active FROM redeem_products WHERE active=true ORDER BY price ASC, id ASC"
        )
    return await p.fetch(
        "SELECT id, code, name, description, price, stock, active FROM redeem_products ORDER BY id ASC"
    )


async def redeem_product(user_id: int, username: str, product_code: str) -> dict[str, Any]:
    p = _require_pool()
    async with p.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO users(user_id, username) VALUES($1, $2)
                ON CONFLICT(user_id) DO UPDATE SET username=$2, updated_at=now()
                """,
                user_id,
                username,
            )
            await conn.execute("INSERT INTO points_balance(user_id) VALUES($1) ON CONFLICT DO NOTHING", user_id)

            product = await conn.fetchrow(
                "SELECT id, code, name, price, stock, active FROM redeem_products WHERE UPPER(code)=UPPER($1) FOR UPDATE",
                product_code,
            )
            if product is None or not product["active"]:
                raise ValueError("product_not_found")
            if product["stock"] <= 0:
                raise ValueError("out_of_stock")

            balance_row = await conn.fetchrow(
                "SELECT balance FROM points_balance WHERE user_id=$1 FOR UPDATE",
                user_id,
            )
            if balance_row["balance"] < product["price"]:
                raise ValueError(f"insufficient_balance:{balance_row['balance']}:{product['price']}")

            new_balance = balance_row["balance"] - product["price"]
            await conn.execute(
                """
                UPDATE points_balance
                SET balance=$2, total_spent=total_spent+$3, updated_at=now()
                WHERE user_id=$1
                """,
                user_id,
                new_balance,
                product["price"],
            )
            await conn.execute(
                "UPDATE redeem_products SET stock=stock-1, updated_at=now() WHERE id=$1",
                product["id"],
            )
            order = await conn.fetchrow(
                """
                INSERT INTO redeem_orders(user_id, product_id, product_code, product_name, price, status)
                VALUES($1, $2, $3, $4, $5, 'pending')
                RETURNING id, created_at
                """,
                user_id,
                product["id"],
                product["code"],
                product["name"],
                product["price"],
            )
            await conn.execute(
                """
                INSERT INTO points_ledger(user_id, change, balance_after, reason_code, detail)
                VALUES($1, $2, $3, 'REDEEM', $4)
                """,
                user_id,
                -product["price"],
                new_balance,
                f"order:{order['id']};product:{product['code']}",
            )
            return {
                "order_id": order["id"],
                "product_code": product["code"],
                "product_name": product["name"],
                "price": product["price"],
                "balance": new_balance,
            }


async def list_user_orders(user_id: int, limit: int = 10) -> list[asyncpg.Record]:
    p = _require_pool()
    return await p.fetch(
        """
        SELECT id, product_name, price, status, note, created_at, updated_at
        FROM redeem_orders
        WHERE user_id=$1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        user_id,
        limit,
    )


async def list_orders(status: str = "pending", limit: int = 20) -> list[asyncpg.Record]:
    p = _require_pool()
    if status.lower() == "all":
        return await p.fetch(
            "SELECT id, user_id, product_name, price, status, note, created_at FROM redeem_orders ORDER BY created_at DESC LIMIT $1",
            limit,
        )
    return await p.fetch(
        """
        SELECT id, user_id, product_name, price, status, note, created_at
        FROM redeem_orders
        WHERE status=$1
        ORDER BY created_at DESC
        LIMIT $2
        """,
        status.lower(),
        limit,
    )


async def update_order_status(order_id: int, status: str, operator_id: int, note: str = "") -> asyncpg.Record | None:
    p = _require_pool()
    return await p.fetchrow(
        """
        UPDATE redeem_orders
        SET status=$2, operator_id=$3, note=$4, updated_at=now()
        WHERE id=$1
        RETURNING id, user_id, product_name, price, status
        """,
        order_id,
        status,
        operator_id,
        note,
    )


async def log_admin_action(operator_id: int, action: str, target_user_id: int | None = None, detail: str = "") -> None:
    p = _require_pool()
    await p.execute(
        "INSERT INTO admin_logs(operator_id, action, target_user_id, detail) VALUES($1, $2, $3, $4)",
        operator_id,
        action,
        target_user_id,
        detail,
    )
