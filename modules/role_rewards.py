import db
async def check_role_rewards(before,after):
 added=set(after.roles)-set(before.roles)
 for role in added:
  async with db.pool.acquire() as c:
   r=await c.fetchrow('select points from role_rewards where role_id=$1',role.id)
   h=await c.fetchval('select 1 from role_reward_history where user_id=$1 and role_id=$2',after.id,role.id)
   if r and not h:
    await c.execute('insert into users(user_id,points) values($1,$2) on conflict(user_id) do update set points=users.points+$2',after.id,r['points'])
    await c.execute('insert into role_reward_history(user_id,role_id) values($1,$2)',after.id,role.id)
