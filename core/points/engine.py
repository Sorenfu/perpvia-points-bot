from database.connection import pool

class PointEngine:
    async def balance(self,user_id):
        async with pool.acquire() as c:
            row=await c.fetchrow('SELECT points FROM users WHERE discord_id=$1',user_id)
        return row['points'] if row else 0

    async def add(self,user_id,amount,source,reason):
        async with pool.acquire() as c:
            await c.execute('INSERT INTO users(discord_id,points) VALUES($1,$2) ON CONFLICT(discord_id) DO UPDATE SET points=users.points+$2',user_id,amount)
            await c.execute('INSERT INTO point_transactions(user_id,amount,source,reason) VALUES($1,$2,$3,$4)',user_id,amount,source,reason)
