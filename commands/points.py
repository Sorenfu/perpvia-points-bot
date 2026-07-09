def register(tree):
    @tree.command(name='points',description='Check points')
    async def points(interaction):
        await interaction.response.send_message('Points online')
