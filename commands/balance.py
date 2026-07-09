def register(tree):
    @tree.command(name='balance',description='balance command')
    async def cmd(interaction):
        await interaction.response.send_message('balance online')
