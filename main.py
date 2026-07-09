import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from commands.loader import load_commands
from checks.startup import validate_env

load_dotenv()
validate_env()

class CommunityOS(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.members=True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)

    async def setup_hook(self):
        load_commands(self.tree)
        guild_id=os.getenv('GUILD_ID')
        if guild_id:
            guild=discord.Object(id=int(guild_id))
            await self.tree.sync(guild=guild)
            print('Guild commands synced')
        else:
            await self.tree.sync()
        print('Commands:',[c.name for c in self.tree.get_commands()])

bot=CommunityOS()

@bot.event
async def on_ready():
    print(f'System Ready: {bot.user}')

bot.run(os.getenv('DISCORD_TOKEN'))
