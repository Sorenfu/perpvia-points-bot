import os,discord
async def reset_sync(bot):
    guild=discord.Object(id=int(os.getenv('GUILD_ID')))
    bot.tree.clear_commands(guild=guild)
    await bot.tree.sync(guild=guild)
    await bot.tree.sync(guild=guild)
    print('Guild commands reset')
