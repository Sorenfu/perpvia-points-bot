import os, discord
from discord import app_commands
from commands.loader import load_commands
from discord.sync import reset_sync

intents=discord.Intents.default()
intents.members=True

class Bot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)
    async def setup_hook(self):
        load_commands(self.tree)
        await reset_sync(self)
        print('Commands:', [c.name for c in self.tree.get_commands()])

bot=Bot()

@bot.event
async def on_ready():
    print(f'Online {bot.user}')

bot.run(os.environ['DISCORD_TOKEN'])
