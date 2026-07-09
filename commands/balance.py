import discord

def register(tree):
    @tree.command(name='balance',description='Check points balance')
    async def balance(interaction:discord.Interaction):
        await interaction.response.send_message('💎 Points: 0')
