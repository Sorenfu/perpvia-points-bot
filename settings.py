# ============================================================
# settings.py - 运营配置区
# ============================================================
# 大多数情况下，你只需要改这里和 Railway 环境变量。
# 真正上线后，商品、活动、任务建议逐步迁移到数据库后台配置。

import os

POINTS_NAME = os.getenv("POINTS_NAME", "PerpPoint")

# Discord 服务器 ID。填了以后斜杠指令会秒同步到指定服务器。
DISCORD_GUILD_ID = int(os.getenv("DISCORD_GUILD_ID", "0") or 0)

# 管理员身份组 ID。拥有此身份组的人可以使用 /admin 系列指令。
ADMIN_ROLE_ID = int(os.getenv("ADMIN_ROLE_ID", "0") or 0)

# 日志频道 ID。发分、扣分、兑换、管理员操作会推送到这里。可留空。
LOG_CHANNEL_ID = int(os.getenv("LOG_CHANNEL_ID", "0") or 0)

# 每日签到奖励
DAILY_POINTS = int(os.getenv("DAILY_POINTS", "20") or 20)
DAILY_STREAK_BONUS_DAYS = int(os.getenv("DAILY_STREAK_BONUS_DAYS", "7") or 7)
DAILY_STREAK_BONUS_POINTS = int(os.getenv("DAILY_STREAK_BONUS_POINTS", "100") or 100)

# ---- 身份组发分映射 ----
# 用户获得下面任一身份组时，Bot 自动发对应积分。每人每身份组只发一次。
# 请把 role_id 改成 Discord 真实 Role ID。
ROLE_GRANTS = [
    {"rule_id": "ROLE_000", "name": "Wayfarer 开户礼", "role_id": 0, "points": 20},
    {"rule_id": "ROLE_001", "name": "Pathfinder Lv5", "role_id": 0, "points": 100},
    {"rule_id": "ROLE_002", "name": "Trailblazer Lv10", "role_id": 0, "points": 300},
    {"rule_id": "ROLE_003", "name": "Momentum Maker Lv15", "role_id": 0, "points": 600},
    {"rule_id": "ROLE_004", "name": "Via Elite Lv20", "role_id": 0, "points": 1000},
]

# 首次部署时可用这里初始化商城商品。
# Bot 启动后会自动 upsert 到数据库。
SEED_PRODUCTS = [
    {
        "code": "VIP_7D",
        "name": "Discord VIP 7 天",
        "description": "兑换后由运营手动发放 VIP 身份组。",
        "price": 300,
        "stock": 100,
        "active": True,
    },
    {
        "code": "NFT_WL",
        "name": "NFT 白名单资格",
        "description": "用于 NFT 活动白名单，兑换后进入人工审核。",
        "price": 1000,
        "stock": 50,
        "active": True,
    },
]
