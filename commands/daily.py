from modules.daily.service import DailyService

def register(tree):
    service=DailyService()
    @tree.command(name='daily',description='Daily checkin')
    async def daily(interaction):
        ok,reward=await service.checkin(interaction.user.id)
        if ok:
            await interaction.response.send_message(f'🎉 Daily +{reward} Points')
        else:
            await interaction.response.send_message('Daily cooldown active')
