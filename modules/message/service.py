from datetime import datetime,timedelta,date
from database.connection import pool
from core.points.engine import PointEngine

class MessageRewardService:
    async def process(self,user_id,content):
        if len(content.strip()) < 10:
            return False
        async with pool.acquire() as c:
            last=await c.fetchval('SELECT created_at FROM message_rewards WHERE user_id=$1 ORDER BY created_at DESC LIMIT 1',user_id)
            total=await c.fetchval('SELECT COALESCE(SUM(amount),0) FROM message_rewards WHERE user_id=$1 AND reward_date=$2',user_id,date.today())
        if last and datetime.utcnow()-last < timedelta(seconds=60):
            return False
        if total>=50:
            return False
        await PointEngine().add(user_id,1,'message','Message Reward')
        async with pool.acquire() as c:
            await c.execute('INSERT INTO message_rewards(user_id,amount) VALUES($1,$2)',user_id,1)
        return True
