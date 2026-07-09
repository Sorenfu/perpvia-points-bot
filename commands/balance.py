def register(tree):
    @tree.command(name='balance',description='Check balance')
    async def balance(interaction):
        await interaction.response.send_message('Balance OK')
