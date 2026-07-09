async def sync_commands(bot):
    await bot.tree.sync()
    print('Commands synced')
