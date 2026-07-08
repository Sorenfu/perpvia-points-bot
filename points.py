from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import db
from settings import DAILY_POINTS, DAILY_STREAK_BONUS_DAYS, DAILY_STREAK_BONUS_POINTS, POINTS_NAME
from bot_logging import send_log


class PointsCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="balance", description="查询你的积分余额")
    async def balance(self, interaction: discord.Interaction) -> None:
        data = await db.get_balance(interaction.user.id, str(interaction.user))
        await interaction.response.send_message(
            f"📊 **你的积分**\n"
            f"当前余额：**{data['balance']} {POINTS_NAME}**\n"
            f"累计获得：{data['total_earned']} {POINTS_NAME}\n"
            f"累计消费：{data['total_spent']} {POINTS_NAME}",
            ephemeral=True,
        )

    @app_commands.command(name="daily", description="每日签到领取积分")
    async def daily(self, interaction: discord.Interaction) -> None:
        result = await db.checkin_daily(
            interaction.user.id,
            str(interaction.user),
            DAILY_POINTS,
            DAILY_STREAK_BONUS_DAYS,
            DAILY_STREAK_BONUS_POINTS,
        )
        if result["already"]:
            await interaction.response.send_message(
                f"你今天已经签到过了。当前连续签到：**{result['streak']} 天**。",
                ephemeral=True,
            )
            return

        bonus_text = f"，其中连续签到奖励 +{result['bonus']}" if result.get("bonus") else ""
        await interaction.response.send_message(
            f"✅ 签到成功，获得 **{result['points']} {POINTS_NAME}**{bonus_text}。\n"
            f"连续签到：**{result['streak']} 天**\n"
            f"当前余额：**{result['balance']} {POINTS_NAME}**",
            ephemeral=True,
        )
        await send_log(
            self.bot,
            "Daily Check-in",
            f"{interaction.user.mention} +{result['points']} {POINTS_NAME}，streak={result['streak']}",
        )

    @app_commands.command(name="leaderboard", description="查看积分排行榜")
    @app_commands.describe(limit="显示人数，默认10，最多25")
    async def leaderboard(self, interaction: discord.Interaction, limit: app_commands.Range[int, 1, 25] = 10) -> None:
        rows = await db.get_leaderboard(limit)
        if not rows:
            await interaction.response.send_message("目前还没有积分数据。", ephemeral=True)
            return
        lines = []
        for index, row in enumerate(rows, start=1):
            name = row["username"] or f"User {row['user_id']}"
            lines.append(f"**{index}.** {name} - **{row['balance']} {POINTS_NAME}**")
        embed = discord.Embed(title="🏆 积分排行榜", description="\n".join(lines), color=0xF1C40F)
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="history", description="查看你的积分流水")
    async def history(self, interaction: discord.Interaction) -> None:
        rows = await db.get_ledger(interaction.user.id, 10)
        if not rows:
            await interaction.response.send_message("你目前还没有积分流水。", ephemeral=True)
            return
        lines = []
        for row in rows:
            sign = "+" if row["change"] > 0 else ""
            lines.append(
                f"`{sign}{row['change']}` | 余额 `{row['balance_after']}` | {row['reason_code']} | {row['detail'] or '-'}"
            )
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(PointsCog(bot))
