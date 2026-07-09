import os, discord
async def sync_debug(bot):
    guild=discord.Object(id=int(os.getenv('GUILD_ID')))
    print('Clearing global commands')
    bot.tree.clear_commands(guild=None)
    await bot.tree.sync()
    print('Sync guild commands')
    await bot.tree.sync(guild=guild)
    print('Sync completed')
