def register(tree,engine):
    @tree.command(name='balance',description='View points')
    async def balance(interaction):
        points=await engine.balance(interaction.user.id)
        await interaction.response.send_message(f'💎 Balance: {points} Points')
