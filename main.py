import os
import discord
from discord import app_commands

import db
from modules import points
from modules import daily


intents = discord.Intents.default()


class GrowthBot(discord.Client):

    def __init__(self):
        super().__init__(
            intents=intents
        )
        self.tree = app_commands.CommandTree(self)


    async def setup_hook(self):

        await db.init_pool()

        await self.tree.sync()

        print("Commands synced")


bot = GrowthBot()


@bot.event
async def on_ready():

    print(
        f"Bot online: {bot.user}"
    )


bot.run(
    os.environ["DISCORD_TOKEN"]
)
