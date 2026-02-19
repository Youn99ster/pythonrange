# HackShop 仿真商城漏洞靶场 - 产品需求文档（PRD）

| 项目 | 内容 |
|---|---|
| 文档版本 | v3.8 |
| 创建日期 | 2025-09-28 |
| 最后更新 | 2026-02-16 |
| 文档状态 | 与当前代码实现对齐 |

## 1. 产品概述
- 产品类型：业务驱动式 Web 安全教学靶场
- 核心目标：在真实电商流程中进行漏洞学习与复现
- 角色：普通用户、管理员

## 2. 功能范围
- 用户认证：注册/登录/找回密码/重置密码
- 商城流程：商品浏览、购物车、下单、支付、订单详情
- 用户中心：地址管理、资产查询、储值券兑换
- 管理后台：商品管理、订单管理、用户管理、储值券、批量导入
- 仿真辅助：模拟收件箱、初始化页面

## 3. 漏洞范围（10个）
| 漏洞ID | 名称 | 状态 |
|---|---|---|
| V-Auth-DoS | 认证拒绝服务 | 已实现 |
| V-Host-Inject | Host 头注入 | 已实现 |
| V-CSRF-Pay | 支付 CSRF | 已实现 |
| V-Race-Condition | 并发兑换竞态 | 已实现 |
| V-IDOR-View | 越权查看订单 | 已实现 |
| V-IDOR-Modify | 越权修改地址 | 已实现 |
| V-SSRF | 后台导入 SSRF | 已实现 |
| V-SQL-Union | SQL 注入（订单详情） | 已实现 |
| V-SSTI | 模板注入（订单详情） | 已实现 |
| V-Admin-AES | 管理员 AES 密钥泄露 | 已实现 |

> 注：`V-SQL-Timing` 已移除，不属于当前范围。

## 4. 技术架构
- Flask + Blueprint 模块化
- MySQL + SQLAlchemy + Flask-Migrate
- Redis 缓存
- Docker Compose（三服务）
- Gunicorn 运行

## 5. 工程化能力（当前）
- 容器健康检查：mysql/redis/web
- MySQL 持久化卷：`mysql_data`
- 启动迁移策略：`db upgrade` + `stamp head` fallback
- 日志：控制台 + 轮转文件（`logs/app.log`）
- 实验脚本：`scripts/seed.py`、`scripts/reset_lab.py`

## 6. 里程碑状态（代码对齐）
| 任务ID | 描述 | 状态 |
|---|---|---|
| ARCH-202 | 商品/订单 API | ✅ |
| ARCH-203 | CSRF/SQL/IDOR-View | ✅ |
| ARCH-204 | SSTI | ✅ |
| ARCH-302 | 兑换竞态 | ✅ |
| ARCH-403 | 导入 SSRF | ✅ |
| ARCH-502 | 收件箱 API | ✅ |

## 7. 验收标准
- `docker compose up -d --build` 后可访问 `127.0.0.1:8000`
- `/setup` 可完成初始化
- 管理后台关键路径可访问并可操作
- 10 个漏洞可在授权环境复现

## 8. 文档历史
- v3.8（2026-02-16）：同步最新启动、健康检查、seed/reset、日志能力
- v3.7（2026-02-16）：修复乱码并重建文档
