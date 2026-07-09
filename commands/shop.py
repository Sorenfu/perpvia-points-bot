def register(tree):
    @tree.command(name='shop',description='Open shop')
    async def shop(interaction):
        await interaction.response.send_message('Shop online')
