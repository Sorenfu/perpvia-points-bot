import db


async def get_balance(user_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            """
            SELECT balance,total_earned,total_spent
            FROM points_balance
            WHERE user_id=$1
            """,
            user_id
        )

    if not row:
        return {
            "balance": 0,
            "total_earned": 0,
            "total_spent": 0
        }

    return dict(row)


async def add_points(user_id, amount, reason, detail=""):
    async with db.pool.acquire() as conn:
        async with conn.transaction():
            await conn.execute(
                """
                INSERT INTO points_balance
                (user_id,balance,total_earned)
                VALUES($1,$2,$2)
                ON CONFLICT(user_id)
                DO UPDATE SET
                balance=points_balance.balance+$2,
                total_earned=points_balance.total_earned+$2
                """,
                user_id,
                amount
            )

            await conn.execute(
                """
                INSERT INTO points_ledger
                (user_id,change_amount,reason_code,detail)
                VALUES($1,$2,$3,$4)
                """,
                user_id,
                amount,
                reason,
                detail
            )
