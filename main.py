import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class CommunityOS(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.members=True
        intents.message_content=True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)

    async def setup_hook(self):
        guild=discord.Object(id=int(os.getenv('GUILD_ID')))
        self.tree.copy_global_to(guild=guild)
        await self.tree.sync(guild=guild)
        print('Commands synced')

bot=CommunityOS()

@bot.event
async def on_ready():
    print(f'Community OS Ready: {bot.user}')

@bot.tree.command(name='balance')
async def balance(interaction):
    await interaction.response.send_message('Balance system ready')

@bot.tree.command(name='daily')
async def daily(interaction):
    await interaction.response.send_message('Daily system ready')

@bot.tree.command(name='shop')
async def shop(interaction):
    await interaction.response.send_message('Shop system ready')

bot.run(os.getenv('DISCORD_TOKEN'))
