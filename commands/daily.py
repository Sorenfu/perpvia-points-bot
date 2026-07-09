def register(tree):
    @tree.command(name='daily',description='daily command')
    async def cmd(interaction):
        await interaction.response.send_message('daily online')
