import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from database.connection import connect
from core.points.engine import PointEngine
from modules.daily.service import DailyService

load_dotenv()

class CommunityOS(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.members=True
        intents.message_content=True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)
        self.points=PointEngine()

    async def setup_hook(self):
        await connect()
        guild=discord.Object(id=int(os.getenv('GUILD_ID')))
        self.tree.copy_global_to(guild=guild)
        synced=await self.tree.sync(guild=guild)
        print('Commands:',[c.name for c in synced])

bot=CommunityOS()

daily_service=DailyService()

@bot.tree.command(name='balance',description='Check balance')
async def balance(interaction):
    value=await bot.points.balance(interaction.user.id)
    await interaction.response.send_message(f'💎 Balance: {value} Points')

@bot.tree.command(name='daily',description='Daily reward')
async def daily(interaction):
    ok,msg=await daily_service.checkin(interaction.user.id)
    await interaction.response.send_message(msg if not ok else f'🎉 +{msg} Points')

@bot.event
async def on_ready():
    print(f'System Ready: {bot.user}')

bot.run(os.getenv('DISCORD_TOKEN'))
