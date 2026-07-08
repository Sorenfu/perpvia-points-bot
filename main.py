import os
import discord
from discord import app_commands
import db

intents = discord.Intents.default()
intents.members = True

class GrowthBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        await db.init_pool()
        await self.tree.sync()
        print("Commands synced")

bot = GrowthBot()

@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")

@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")

@bot.tree.command(name="balance", description="Check points balance")
async def balance(interaction: discord.Interaction):
    data = await db.get_balance(interaction.user.id)
    await interaction.response.send_message(
        f"Balance: {data['balance']} points",
        ephemeral=True
    )

bot.run(os.environ["DISCORD_TOKEN"])
