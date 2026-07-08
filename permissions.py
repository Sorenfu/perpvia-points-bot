import discord
from settings import ADMIN_ROLE_ID


def is_admin(member: discord.Member | discord.User) -> bool:
    if not isinstance(member, discord.Member):
        return False
    if member.guild_permissions.administrator:
        return True
    if ADMIN_ROLE_ID == 0:
        return False
    return any(role.id == ADMIN_ROLE_ID for role in member.roles)
