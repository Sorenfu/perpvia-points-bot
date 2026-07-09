import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from commands.loader import load_commands
from discord.sync import sync_debug
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
        print('Application ID:',self.application_id)
        print('Guild ID:',os.getenv('GUILD_ID'))
        load_commands(self.tree)
        print('Loaded:',[c.name for c in self.tree.get_commands()])
        await sync_debug(self)

bot=CommunityOS()

@bot.event
async def on_ready():
    print('System Ready:',bot.user)

bot.run(os.environ['DISCORD_TOKEN'])
