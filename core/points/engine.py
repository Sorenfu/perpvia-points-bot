from database.connection import pool
class PointEngine:
 async def balance(self,user_id):
  async with pool.acquire() as c:
   row=await c.fetchrow('SELECT points FROM users WHERE discord_id=$1',user_id)
  return row['points'] if row else 0
