from __future__ import annotations

import discord
from discord import app_commands
from discord.ext import commands

import db
from settings import POINTS_NAME
from bot_logging import send_log
from bot_permissions import is_admin


def admin_only():
    async def predicate(interaction: discord.Interaction) -> bool:
        if is_admin(interaction.user):
            return True
        raise app_commands.CheckFailure("admin_only")
    return app_commands.check(predicate)


class AdminCog(commands.Cog):
    admin = app_commands.Group(name="admin", description="管理员运营指令")

    def __init__(self, bot: commands.Bot) -> None:
        self.bot = bot

    async def cog_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, app_commands.CheckFailure):
            if interaction.response.is_done():
                await interaction.followup.send("你没有权限使用该指令。", ephemeral=True)
            else:
                await interaction.response.send_message("你没有权限使用该指令。", ephemeral=True)
            return
        raise error

    @admin.command(name="addpoints", description="给用户增加积分")
    @admin_only()
    async def addpoints(self, interaction: discord.Interaction, user: discord.Member, amount: app_commands.Range[int, 1, 1000000], reason: str = "admin_add") -> None:
        result = await db.change_points(user.id, amount, "ADMIN_ADD", reason, operator_id=interaction.user.id, username=str(user))
        await db.log_admin_action(interaction.user.id, "ADD_POINTS", user.id, f"amount={amount};reason={reason}")
        await interaction.response.send_message(
            f"✅ 已给 {user.mention} 增加 **{amount} {POINTS_NAME}**，当前余额：{result['balance']}。",
            ephemeral=True,
        )
        await send_log(self.bot, "Admin Add Points", f"{interaction.user.mention} -> {user.mention}: +{amount} {POINTS_NAME}. {reason}")

    @admin.command(name="removepoints", description="扣除用户积分")
    @admin_only()
    async def removepoints(self, interaction: discord.Interaction, user: discord.Member, amount: app_commands.Range[int, 1, 1000000], reason: str = "admin_remove") -> None:
        try:
            result = await db.change_points(user.id, -amount, "ADMIN_REMOVE", reason, operator_id=interaction.user.id, username=str(user))
        except ValueError as exc:
            if str(exc).startswith("insufficient_balance"):
                current = str(exc).split(":")[1]
                await interaction.response.send_message(f"扣分失败，{user.mention} 当前只有 {current} {POINTS_NAME}。", ephemeral=True)
                return
            raise
        await db.log_admin_action(interaction.user.id, "REMOVE_POINTS", user.id, f"amount={amount};reason={reason}")
        await interaction.response.send_message(
            f"✅ 已扣除 {user.mention} **{amount} {POINTS_NAME}**，当前余额：{result['balance']}。",
            ephemeral=True,
        )
        await send_log(self.bot, "Admin Remove Points", f"{interaction.user.mention} -> {user.mention}: -{amount} {POINTS_NAME}. {reason}", color=0xE74C3C)

    @admin.command(name="products", description="查看全部商城商品")
    @admin_only()
    async def products(self, interaction: discord.Interaction) -> None:
        rows = await db.list_products(active_only=False)
        if not rows:
            await interaction.response.send_message("当前没有商品。", ephemeral=True)
            return
        lines = [
            f"`{r['code']}` | {r['name']} | {r['price']} {POINTS_NAME} | stock={r['stock']} | active={r['active']}"
            for r in rows
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @admin.command(name="setproduct", description="新增或修改商城商品")
    @admin_only()
    async def setproduct(
        self,
        interaction: discord.Interaction,
        code: str,
        name: str,
        price: app_commands.Range[int, 1, 10000000],
        stock: app_commands.Range[int, 0, 1000000],
        active: bool = True,
        description: str = "",
    ) -> None:
        await db.upsert_product(code.upper(), name, description, price, stock, active)
        await db.log_admin_action(interaction.user.id, "SET_PRODUCT", detail=f"code={code};price={price};stock={stock};active={active}")
        await interaction.response.send_message(f"✅ 商品 `{code.upper()}` 已保存。", ephemeral=True)
        await send_log(self.bot, "Product Updated", f"{interaction.user.mention} saved `{code.upper()}`: {name}, {price} {POINTS_NAME}, stock={stock}, active={active}")

    @admin.command(name="orders", description="查看兑换订单")
    @admin_only()
    async def orders(self, interaction: discord.Interaction, status: str = "pending", limit: app_commands.Range[int, 1, 50] = 20) -> None:
        rows = await db.list_orders(status, limit)
        if not rows:
            await interaction.response.send_message("没有找到订单。", ephemeral=True)
            return
        lines = [
            f"#{r['id']} | <@{r['user_id']}> | {r['product_name']} | {r['price']} {POINTS_NAME} | `{r['status']}` | {r['note'] or '-'}"
            for r in rows
        ]
        await interaction.response.send_message("\n".join(lines), ephemeral=True)

    @admin.command(name="orderstatus", description="更新兑换订单状态")
    @admin_only()
    async def orderstatus(self, interaction: discord.Interaction, order_id: int, status: str, note: str = "") -> None:
        allowed = {"pending", "processing", "completed", "cancelled"}
        status = status.lower()
        if status not in allowed:
            await interaction.response.send_message("状态只能是 pending / processing / completed / cancelled。", ephemeral=True)
            return
        row = await db.update_order_status(order_id, status, interaction.user.id, note)
        if row is None:
            await interaction.response.send_message("没有找到该订单。", ephemeral=True)
            return
        await db.log_admin_action(interaction.user.id, "ORDER_STATUS", row["user_id"], f"order={order_id};status={status};note={note}")
        await interaction.response.send_message(f"✅ 订单 #{order_id} 已更新为 `{status}`。", ephemeral=True)
        await send_log(self.bot, "Order Status Updated", f"Order #{order_id} -> `{status}` by {interaction.user.mention}. {note}")


async def setup(bot: commands.Bot) -> None:
    await bot.add_cog(AdminCog(bot))
