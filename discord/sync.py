import discord

async def sync_guild_commands(bot,guild_id):
    guild=discord.Object(id=guild_id)
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync(guild=guild)
    await bot.tree.sync(guild=guild)
    print('Guild commands synced')
