from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import db
from settings import POINTS_NAME
from bot_logging import send_log


class ShopCog(commands.Cog):
    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    @app_commands.command(name="shop", description="查看积分商城")
    async def shop(self, interaction: discord.Interaction) -> None:
        products = await db.list_products(active_only=True)
        if not products:
            await interaction.response.send_message("商城暂无可兑换商品。", ephemeral=True)
            return
        embed = discord.Embed(title="🎁 积分商城", description="使用 `/redeem 商品代码` 兑换。", color=0x3498DB)
        for item in products:
            status = "有库存" if item["stock"] > 0 else "已售罄"
            embed.add_field(
                name=f"{item['name']} | `{item['code']}`",
                value=(
                    f"价格：**{item['price']} {POINTS_NAME}**\n"
                    f"库存：{item['stock']}（{status}）\n"
                    f"说明：{item['description'] or '-'}"
                ),
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)

    @app_commands.command(name="redeem", description="兑换积分商城商品")
    @app_commands.describe(product_code="商品代码，例如 VIP_7D")
    async def redeem(self, interaction: discord.Interaction, product_code: str) -> None:
        await interaction.response.defer(ephemeral=True)
        try:
            result = await db.redeem_product(interaction.user.id, str(interaction.user), product_code)
        except ValueError as exc:
            msg = str(exc)
            if msg.startswith("insufficient_balance"):
                parts = msg.split(":")
                await interaction.followup.send(
                    f"积分不足。当前余额：{parts[1]} {POINTS_NAME}，商品价格：{parts[2]} {POINTS_NAME}。",
                    ephemeral=True,
                )
            elif msg == "out_of_stock":
                await interaction.followup.send("该商品库存不足，暂时无法兑换。", ephemeral=True)
            else:
                await interaction.followup.send("没有找到该商品，或该商品已下架。", ephemeral=True)
            return

        await interaction.followup.send(
            f"✅ 兑换成功，订单号：**#{result['order_id']}**\n"
            f"商品：**{result['product_name']}**\n"
            f"消耗：**{result['price']} {POINTS_NAME}**\n"
            f"当前余额：**{result['balance']} {POINTS_NAME}**\n"
            f"订单状态：待运营处理。",
            ephemeral=True,
        )
        await send_log(
            self.bot,
            "Redeem Order",
            f"{interaction.user.mention} redeemed **{result['product_name']}** for {result['price']} {POINTS_NAME}. Order #{result['order_id']}",
            color=0x9B59B6,
        )

    @app_commands.command(name="myorders", description="查看我的兑换订单")
    async def myorders(self, interaction: discord.Interaction) -> None:
        rows = await db.list_user_orders(interaction.user.id, 10)
        if not rows:
            await interaction.response.send_message("你还没有兑换订单。", ephemeral=True)
            return
        lines = [
            f"#{r['id']} | {r['product_name']} | {r['price']} {POINTS_NAME} | `{r['status']}` | {r['note'] or '-'}"
            for r in rows
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(ShopCog(bot))
