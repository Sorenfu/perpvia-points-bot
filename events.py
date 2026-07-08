from __future__ import annotations

import discord
from discord.ext import commands

import db
from settings import POINTS_NAME, ROLE_GRANTS
from bot_logging import send_log

ROLE_MAP = {g["role_id"]: g for g in ROLE_GRANTS if g.get("role_id")}


class EventsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @commands.Cog.listener()
    async def on_member_update(self, before: discord.Member, after: discord.Member) -> None:
        before_ids = {role.id for role in before.roles}
        added_roles = [role for role in after.roles if role.id not in before_ids]

        for role in added_roles:
            rule = ROLE_MAP.get(role.id)
            if not rule:
                continue
            try:
                granted = await db.grant_role_points_once(
                    user_id=after.id,
                    username=str(after),
                    role_id=role.id,
                    points=int(rule["points"]),
                    rule_id=rule["rule_id"],
                    role_name=rule["name"],
                )
                if not granted:
                    continue
                try:
                    await after.send(
                        f"🎉 恭喜！你因获得 **{rule['name']}** 身份组，获得 **{rule['points']} {POINTS_NAME}**。\n"
                        f"可使用 `/balance` 查看积分，使用 `/shop` 查看商城。"
                    )
                except discord.Forbidden:
                    pass
                await send_log(
                    self.bot,
                    "Role Reward Granted",
                    f"{after.mention} got **{rule['name']}** and earned +{rule['points']} {POINTS_NAME}.",
                )
            except Exception as exc:
                print(f"Role grant failed for {after} / {role}: {exc}")
                await send_log(
                    self.bot,
                    "Role Reward Error",
                    f"{after.mention} / {role.name}: `{exc}`",
                    color=0xE74C3C,
                )


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(EventsCog(bot))
