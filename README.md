# Discord Growth Bot v2

这是基于原积分机器人重构后的版本，定位是 Discord 社区增长与积分商城机器人。

## 已包含功能

- 身份组自动发积分，每人每身份组只发一次
- `/balance` 查询积分
- `/daily` 每日签到，支持连续签到奖励
- `/leaderboard` 积分排行榜
- `/history` 用户积分流水
- `/shop` 查看积分商城
- `/redeem 商品代码` 兑换商品
- `/myorders` 查看自己的兑换订单
- `/admin addpoints` 管理员加积分
- `/admin removepoints` 管理员扣积分，防止负数余额
- `/admin setproduct` 新增或修改商品
- `/admin products` 查看商品
- `/admin orders` 查看订单
- `/admin orderstatus` 更新订单状态
- 日志频道推送：发分、签到、兑换、管理员操作
- PostgreSQL 事务保护：扣分、库存、兑换订单保持一致

## 部署到 Railway

1. 上传项目文件到 GitHub。
2. Railway 创建 PostgreSQL。
3. Railway 项目添加环境变量：

```bash
DISCORD_TOKEN=你的DiscordBotToken
DATABASE_URL=Railway PostgreSQL连接串
DISCORD_GUILD_ID=你的服务器ID
ADMIN_ROLE_ID=管理员身份组ID
LOG_CHANNEL_ID=日志频道ID
POINTS_NAME=PerpPoint
```

4. Discord Developer Portal 中开启：
   - SERVER MEMBERS INTENT

5. Railway 使用 Procfile 启动：

```bash
worker: python main.py
```

## 运营配置

### 身份组发分

编辑 `settings.py`：

```python
ROLE_GRANTS = [
    {"rule_id": "ROLE_001", "name": "Pathfinder Lv5", "role_id": 123456789, "points": 100},
]
```

### 商城商品

首次初始化可编辑 `SEED_PRODUCTS`。上线后建议使用：

```text
/admin setproduct
```

直接在 Discord 中配置商品。

## 重要说明

这个版本已经解决原 MVP 中最关键的运营问题：

- 原代码只有加分，没有扣分与商城兑换闭环。
- 现在所有积分变化统一走 `change_points()`。
- 扣分时会验证余额，不允许出现负数。
- 商品兑换时会在一个数据库事务中完成扣分、减库存、创建订单、写流水。
- 管理员操作与用户兑换都会进入日志频道，方便运营追踪。

## 下一阶段建议

- 邀请奖励系统
- 任务系统：Twitter、钱包绑定、交易任务
- 抽奖系统：积分门槛、白名单、库存奖品
- 赛季排行榜与自动结算
- Web 后台配置商品、任务、活动
