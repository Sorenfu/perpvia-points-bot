# ============================================================
# main.py - Discord Growth Bot v2 Flat
# ============================================================

import os

import discord
from discord.ext import commands
from dotenv import load_dotenv

import db
from settings import DISCORD_GUILD_ID, SEED_PRODUCTS

load_dotenv()

EXTENSIONS = [
    "points",
    "shop",
    "admin",
    "events",
]


class GrowthBot(commands.Bot):
    def __init__(self) -> None:
        intents = discord.Intents.default()
        intents.members = True
        intents.guilds = True
        super().__init__(command_prefix="!", intents=intents)

    async def setup_hook(self) -> None:
        await db.init_pool()
        await db.seed_products(SEED_PRODUCTS)

        for ext in EXTENSIONS:
            await self.load_extension(ext)

        if DISCORD_GUILD_ID:
            guild = discord.Object(id=DISCORD_GUILD_ID)
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Slash commands synced to guild {DISCORD_GUILD_ID}")
        else:
            await self.tree.sync()
            print("Global slash commands synced")

    async def close(self) -> None:
        await db.close_pool()
        await super().close()


bot = GrowthBot()


@bot.event
async def on_ready() -> None:
    print(f"Bot online as {bot.user}")


def main() -> None:
    token = os.getenv("DISCORD_TOKEN")
    if not token:
        raise SystemExit("Missing DISCORD_TOKEN")
    if not os.getenv("DATABASE_URL"):
        raise SystemExit("Missing DATABASE_URL")
    bot.run(token)


if __name__ == "__main__":
    main()
