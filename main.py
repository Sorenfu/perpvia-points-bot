import os
import discord
from discord import app_commands
from dotenv import load_dotenv
from commands.loader import load_commands

load_dotenv()

class CommunityOS(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.members=True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)

    async def setup_hook(self):
        load_commands(self.tree)
        print('Loaded Commands:',[c.name for c in self.tree.get_commands()])

    async def on_ready(self):
        guild=discord.Object(id=int(os.getenv('GUILD_ID')))
        self.tree.copy_global_to(guild=guild)
        synced=await self.tree.sync(guild=guild)
        print('Discord Accepted Commands:',[c.name for c in synced])
        print('Command Count:',len(synced))
        print(f'System Ready: {self.user}')

bot=CommunityOS()
bot.run(os.getenv('DISCORD_TOKEN'))
