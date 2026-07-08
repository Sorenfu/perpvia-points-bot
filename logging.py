import discord
from discord.ext import commands
from settings import LOG_CHANNEL_ID


async def send_log(bot: commands.Bot, title: str, description: str, *, color: int = 0x2ECC71) -> None:
    if not LOG_CHANNEL_ID:
        return
    channel = bot.get_channel(LOG_CHANNEL_ID)
    if channel is None:
        try:
            channel = await bot.fetch_channel(LOG_CHANNEL_ID)
        except Exception:
            return
    if not hasattr(channel, "send"):
        return
    embed = discord.Embed(title=title, description=description, color=color)
    await channel.send(embed=embed)
