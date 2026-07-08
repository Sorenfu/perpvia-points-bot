from datetime import date
import db

async def checkin(user_id):
    async with db.pool.acquire() as conn:
        row = await conn.fetchrow(
            "SELECT last_checkin FROM daily_checkin WHERE user_id=$1",
            user_id
        )
        if row and row["last_checkin"] == date.today():
            return "Already checked in today."
        await conn.execute(
            "INSERT INTO daily_checkin(user_id,last_checkin,streak) VALUES($1,$2,1) ON CONFLICT(user_id) DO UPDATE SET last_checkin=$2",
            user_id, date.today()
        )
    from modules.points import add_points
    await add_points(user_id,20,"daily_checkin")
    return "Daily check-in +20 PerpPoint"
