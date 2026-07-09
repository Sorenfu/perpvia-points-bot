import os
import discord
from discord import app_commands
from dotenv import load_dotenv

load_dotenv()

class CommunityOS(discord.Client):
    def __init__(self):
        intents=discord.Intents.default()
        intents.members=True
        super().__init__(intents=intents)
        self.tree=app_commands.CommandTree(self)

    async def setup_hook(self):
        print('Loading modules...')
        await self.tree.sync(guild=discord.Object(id=int(os.getenv('GUILD_ID'))))
        print('Commands synced')

bot=CommunityOS()

@bot.event
async def on_ready():
    print(f'Discord Connected: {bot.user}')
    print('System Ready')

@bot.tree.command(name='balance',description='Check points')
async def balance(interaction):
    await interaction.response.send_message('Balance: 0 Points')

@bot.tree.command(name='daily',description='Daily checkin')
async def daily(interaction):
    await interaction.response.send_message('Daily +20 Points')

@bot.tree.command(name='shop',description='Open shop')
async def shop(interaction):
    await interaction.response.send_message('Shop Ready')

bot.run(os.getenv('DISCORD_TOKEN'))
