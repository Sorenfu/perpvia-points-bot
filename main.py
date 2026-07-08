import os, discord
from discord import app_commands
from dotenv import load_dotenv
import db
from modules import role_rewards
load_dotenv()
intents=discord.Intents.default(); intents.members=True
class Bot(discord.Client):
 def __init__(self): super().__init__(intents=intents); self.tree=app_commands.CommandTree(self)
 async def setup_hook(self): await db.init_pool(); await self.tree.sync()
bot=Bot()
@bot.event
async def on_member_update(before,after): await role_rewards.check_role_rewards(before,after)
@bot.event
async def on_ready(): print('online',bot.user)
bot.run(os.environ['DISCORD_TOKEN'])
