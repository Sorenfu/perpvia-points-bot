import discord

def register(tree):
    @tree.command(name='points',description='Check points')
    async def points(interaction:discord.Interaction):
        await interaction.response.send_message('💎 Points: 0')
