def register(tree):
    @tree.command(name='shop',description='shop command')
    async def cmd(interaction):
        await interaction.response.send_message('shop online')
