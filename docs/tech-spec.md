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
- 健康检查：MySQL / Redis / Web
- MySQL 持久化卷：`mysql_data`
- 可选启动脚本：`SEED_ON_BOOT`、`RESET_LAB_ON_BOOT`
- 应用日志：控制台 + `logs/app.log`（轮转）

## 6. 实验脚本
- `scripts/seed.py`：导入管理员、测试用户与演示商品
- `scripts/reset_lab.py`：清理业务数据与缓存后重建数据
- `scripts/ensure_indexes.py`：创建数据库索引（启动时自动执行）
- 默认种子账号：`admin/admin123`、`alice@test.com/alice123`

## 7. 漏洞实现映射（摘要）
- V-Auth-DoS：`authenticate_user`
- V-Host-Inject：`send_reset_url`
- V-CSRF-Pay：`order.checkout`
- V-Race-Condition：`user.voucher_redeem` / `order.checkout`
- V-IDOR-Modify：`user.edit_address` / `user.delete_address`
- V-IDOR-View / V-SQL-Union / V-SSTI：`user.order_detail` 相关链路
- V-SSRF：`admin.products_batch_import`
- V-Admin-AES：`admin.login` 前后端链路

## 8. 代码质量治理记录
- `auth` 控制器用户可见消息已统一规范
- `auth` 相关模板（注册/找回/重置）已重建为稳定文本版本
- 管理端与主站关键模板已完成文案与注释整理
- Sonar 非安全项优化遵循“不破坏靶场漏洞链路”的约束

## 9. 当前状态
- 核心业务：已实现
- 漏洞场景：10 个已实现且保留
- 工程可运行性：具备稳定启动与重置能力
- 测试策略：保留最小自动化测试（基础 smoke），以靶场手动验证为主

## 10. 文档历史
- 2026-02-20：补充种子账号说明并与容器运行口径对齐
- 2026-02-20：统一质量描述，移除特定表述并按当前代码状态更新
- 2026-02-16：同步启动策略与脚本能力
