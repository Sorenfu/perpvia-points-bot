import os
import discord
from discord import app_commands
from dotenv import load_dotenv

import db
from modules import points, daily

load_dotenv()

intents = discord.Intents.default()
intents.members = True


class GrowthBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):

    await db.init_pool()

    guild_id = os.environ.get("DISCORD_GUILD_ID")

    if guild_id:
        guild = discord.Object(id=int(guild_id))

        self.tree.copy_global_to(guild=guild)

        await self.tree.sync(guild=guild)

        print(f"Commands synced to guild {guild_id}")

    else:
        await self.tree.sync()

        print("Global commands synced")
        print("Commands synced")


bot = GrowthBot()


@bot.event
async def on_ready():
    print(f"Bot online: {bot.user}")


@bot.tree.command(name="ping", description="Check bot status")
async def ping(interaction: discord.Interaction):
    await interaction.response.send_message("🏓 Pong!")


@bot.tree.command(name="balance", description="Check points")
async def balance(interaction: discord.Interaction):
    data = await points.get_balance(interaction.user.id)
    await interaction.response.send_message(
        f"PerpPoint Balance: {data['balance']}\n"
        f"Earned: {data['total_earned']}\n"
        f"Spent: {data['total_spent']}",
        ephemeral=True
    )


@bot.tree.command(name="daily", description="Daily check in")
async def daily_cmd(interaction: discord.Interaction):
    result = await daily.checkin(interaction.user.id)
    await interaction.response.send_message(result, ephemeral=True)


token = os.environ.get("DISCORD_TOKEN")
if not token:
    raise RuntimeError("Missing DISCORD_TOKEN")

bot.run(token)
