def register(tree):
    @tree.command(name='daily',description='Daily reward')
    async def daily(interaction):
        await interaction.response.send_message('Daily OK')
