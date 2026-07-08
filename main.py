import os
import discord
from discord import app_commands
from dotenv import load_dotenv

import db
from modules import points
from modules import daily

load_dotenv()


# ==========================
# Discord Intents
# ==========================

intents = discord.Intents.default()
intents.members = True


# ==========================
# Bot Client
# ==========================

class GrowthBot(discord.Client):

    def __init__(self):
        super().__init__(
            intents=intents
        )

        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self):

        print("Initializing database...")

        await db.init_pool()


        # Discord Command Sync
        guild_id = os.environ.get(
            "DISCORD_GUILD_ID"
        )


        if guild_id:

            guild = discord.Object(
                id=int(guild_id)
            )

            self.tree.copy_global_to(
                guild=guild
            )

            await self.tree.sync(
                guild=guild
            )

            print(
                f"Commands synced to guild {guild_id}"
            )


        else:

            await self.tree.sync()

            print(
                "Global commands synced"
            )



bot = GrowthBot()



# ==========================
# Bot Ready
# ==========================

@bot.event
async def on_ready():

    print(
        f"Bot online: {bot.user}"
    )



# ==========================
# Ping
# ==========================

@bot.tree.command(
    name="ping",
    description="Check bot status"
)
async def ping(
    interaction: discord.Interaction
):

    await interaction.response.send_message(
        "🏓 Pong!"
    )



# ==========================
# Balance
# ==========================

@bot.tree.command(
    name="balance",
    description="Check your PerpPoint balance"
)
async def balance(
    interaction: discord.Interaction
):

    data = await points.get_balance(
        interaction.user.id
    )


    await interaction.response.send_message(

        f"🎯 **PerpPoint**\n\n"
        f"Current Balance: {data['balance']}\n"
        f"Total Earned: {data['total_earned']}\n"
        f"Total Spent: {data['total_spent']}",

        ephemeral=True
    )



# ==========================
# Daily Check-in
# ==========================

@bot.tree.command(
    name="daily",
    description="Daily check-in reward"
)
async def daily_command(
    interaction: discord.Interaction
):

    result = await daily.checkin(
        interaction.user.id
    )


    await interaction.response.send_message(

        result,

        ephemeral=True
    )



# ==========================
# Start Bot
# ==========================

token = os.environ.get(
    "DISCORD_TOKEN"
)


if not token:

    raise RuntimeError(
        "Missing DISCORD_TOKEN"
    )


bot.run(
    token
)
