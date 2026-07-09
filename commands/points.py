def register(tree):
    @tree.command(name='points',description='points command')
    async def cmd(interaction):
        await interaction.response.send_message('points online')
