# HackShop 技术方案（后端与数据设计）

## 1. 技术选型
- Python + Flask
- SQLAlchemy + Flask-Migrate
- MySQL 8.0
- Redis 6
- Gunicorn

## 2. 模块划分
- `main`：首页、搜索、收件箱、初始化
- `auth`：注册、登录、找回、重置
- `order`：购物车、下单、支付
- `user`：个人中心、地址、资产、订单详情
- `admin`：后台登录、商品/订单/用户/券管理、批量导入

## 3. 数据模型
- 用户与权限：`User`、`Admin`
- 商品域：`Goods`、`GoodsImage`、`GoodsSpec`
- 交易域：`CartItem`、`Order`、`OrderItem`
- 地址与资产：`Address`、`Voucher`
- 辅助：`MailLog`

## 4. 启动链路（当前）
1. Docker Compose 启动 `mysql`、`redis`、`web`
2. 依赖健康检查通过后启动 `web`
3. `start.sh` 等待 MySQL 可连通
4. 执行 `flask db upgrade`
5. 若迁移冲突，尝试 `flask db stamp head` 后重试
6. Gunicorn 启动服务

## 5. 运维能力
- `restart: unless-stopped`
- 健康检查：MySQL/Redis/Web
- MySQL 持久化卷：`mysql_data`
- 可选启动脚本：`SEED_ON_BOOT`、`RESET_LAB_ON_BOOT`
- 应用日志：控制台 + `logs/app.log`（轮转）

## 6. 实验脚本
- `scripts/seed.py`：导入商品与实验基础数据
- `scripts/reset_lab.py`：清理业务数据与缓存后重建数据

## 7. 漏洞实现映射（摘要）
- V-Auth-DoS：`authenticate_user`
- V-Host-Inject：`SendResetUrl`
- V-CSRF-Pay：`order.checkout`
- V-Race-Condition：`user.voucher_redeem`
- V-IDOR-Modify：`user.edit_address` / `user.delete_address`
- V-IDOR-View / V-SQL-Union / V-SSTI：`user.order_detail` 相关链路
- V-SSRF：`admin.products_batch_import`
- V-Admin-AES：`admin.login` 前后端链路

## 8. 当前状态
- 核心业务：已实现
- 漏洞场景：10个已实现
- 工程可运行性：已具备稳定启动与重置能力
- 自动化测试：基础 smoke 已有，可继续扩展

## 9. 文档历史
- 2026-02-16：同步启动策略与脚本能力
