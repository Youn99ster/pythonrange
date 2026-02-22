# HackShop 系统架构与漏洞设计说明

## 1. 系统架构

### 1.1 部署架构

```
┌─────────────────────────────────────────────────────┐
│                  Docker Compose                      │
│                                                      │
│  ┌──────────┐    ┌──────────┐    ┌──────────┐       │
│  │   Web    │    │  MySQL   │    │  Redis   │       │
│  │ (Flask + │───▶│   8.0    │    │    6     │       │
│  │ Gunicorn)│    │          │    │          │       │
│  │  :8000   │    │  :3306   │    │  :6379   │       │
│  └────┬─────┘    └──────────┘    └─────┬────┘       │
│       │                                │             │
│       └────────────────────────────────┘             │
│              Session / Cache                         │
└─────────────────────────────────────────────────────┘
```

### 1.2 应用架构（MVC）

```
┌─────────────────────────────────────────────┐
│                  Flask App                   │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │           Controller Layer           │    │
│  │  main / auth / order / user / admin  │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────▼──────────────────────┐    │
│  │            Model Layer               │    │
│  │  User / Goods / Order / Address ...  │    │
│  │         (SQLAlchemy ORM)             │    │
│  └──────────────┬──────────────────────┘    │
│                 │                            │
│  ┌──────────────▼──────────────────────┐    │
│  │          Utils / Services            │    │
│  │  Redis · Logging · AES · Tools       │    │
│  └─────────────────────────────────────┘    │
│                                              │
│  ┌─────────────────────────────────────┐    │
│  │           View Layer                 │    │
│  │     Jinja2 Templates + Static        │    │
│  │     (Bootstrap 5 + JavaScript)       │    │
│  └─────────────────────────────────────┘    │
└─────────────────────────────────────────────┘
```

### 1.3 数据流

```
Browser ──HTTP──▶ Gunicorn ──WSGI──▶ Flask Router
                                        │
                              ┌─────────▼─────────┐
                              │  Blueprint Handler  │
                              └─────────┬─────────┘
                                        │
                         ┌──────────────┼──────────────┐
                         ▼              ▼              ▼
                    SQLAlchemy       Redis          Jinja2
                    (MySQL)        (Cache)        (Render)
                         │              │              │
                         └──────────────┼──────────────┘
                                        ▼
                                   HTTP Response
```

## 2. 漏洞设计说明

本平台共设计 10 个漏洞，覆盖 OWASP Top 10 中的多个类别。每个漏洞均嵌入真实业务流程，避免"题目化"设计。

### 2.1 V-Auth-DoS — 认证拒绝服务

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A07:2021 - Identification and Authentication Failures |
| 漏洞位置 | `app/utils/tools.py` → `authenticate_user()` |
| 设计原理 | 登录验证使用数据库全表查询匹配用户名，未对登录频率做有效限制。攻击者可通过高频请求消耗数据库连接池资源，导致合法用户无法登录 |
| 教学目标 | 理解认证接口的资源消耗风险，学习速率限制（Rate Limiting）和账户锁定策略 |
| 触发方式 | 对 `/login` 接口发起高并发请求 |

### 2.2 V-Host-Inject — Host 头注入

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A05:2021 - Security Misconfiguration |
| 漏洞位置 | `app/utils/tools.py` → `send_reset_url()` |
| 设计原理 | 密码重置链接使用请求中的 Host 头拼接 URL，未校验 Host 值。攻击者可篡改 Host 头，使受害者收到指向恶意服务器的重置链接 |
| 教学目标 | 理解 HTTP Host 头的可控性，学习白名单校验和固定域名配置 |
| 触发方式 | 在忘记密码请求中修改 Host 头为攻击者控制的域名 |

### 2.3 V-CSRF-Pay — 支付 CSRF

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A01:2021 - Broken Access Control |
| 漏洞位置 | `app/controller/order.py` → `checkout` |
| 设计原理 | 支付接口未使用 CSRF Token 保护（`WTF_CSRF_ENABLED = False`）。攻击者可构造恶意页面，诱导已登录用户自动发起支付请求 |
| 教学目标 | 理解 CSRF 攻击原理，学习 CSRF Token、SameSite Cookie 等防御手段 |
| 触发方式 | 构造包含自动提交表单的恶意 HTML 页面 |

### 2.4 V-Race-Condition — 竞态条件

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A04:2021 - Insecure Design |
| 漏洞位置 | `app/controller/user.py` → `voucher_redeem`；`app/controller/order.py` → `checkout` |
| 设计原理 | 储值券兑换和支付扣减操作采用"先读后写"模式，未使用数据库锁或原子操作。并发请求可在余额检查与扣减之间插入，导致重复兑换或超额支付 |
| 教学目标 | 理解 TOCTOU（Time-of-Check to Time-of-Use）问题，学习悲观锁、乐观锁和数据库事务隔离级别 |
| 触发方式 | 使用并发工具（如 Burp Intruder）同时发送多个兑换/支付请求 |

### 2.5 V-IDOR-View — 越权查看订单

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A01:2021 - Broken Access Control |
| 漏洞位置 | `app/controller/user.py` → `order_detail` |
| 设计原理 | 订单详情接口仅通过订单 ID 查询，未校验当前用户是否为订单所有者。攻击者可遍历订单 ID 查看其他用户的订单信息 |
| 教学目标 | 理解 IDOR（Insecure Direct Object Reference）漏洞，学习基于所有权的访问控制 |
| 触发方式 | 修改 URL 中的订单 ID 参数为其他用户的订单 ID |

### 2.6 V-IDOR-Modify — 越权修改地址

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A01:2021 - Broken Access Control |
| 漏洞位置 | `app/controller/user.py` → `edit_address` / `delete_address` |
| 设计原理 | 地址编辑和删除接口未校验地址是否属于当前用户，仅凭地址 ID 操作。攻击者可修改或删除其他用户的收货地址 |
| 教学目标 | 理解水平越权与垂直越权的区别，学习对象级别的权限校验 |
| 触发方式 | 修改请求中的地址 ID 为其他用户的地址 ID |

### 2.7 V-SSRF — 服务端请求伪造

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A10:2021 - Server-Side Request Forgery |
| 漏洞位置 | `app/controller/admin.py` → `products_batch_import` |
| 设计原理 | 批量导入功能接受用户提供的 URL 并在服务端发起请求下载文件，未对目标地址做限制。攻击者可利用此功能探测内网服务或读取内部资源 |
| 教学目标 | 理解 SSRF 攻击面（内网探测、云元数据读取），学习 URL 白名单和网络隔离策略 |
| 触发方式 | 在批量导入 URL 中填入内网地址（如 `http://127.0.0.1:6379`） |

### 2.8 V-SQL-Union — SQL 注入

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A03:2021 - Injection |
| 漏洞位置 | `app/controller/user.py` → `order_detail` 相关链路 |
| 设计原理 | 订单详情查询使用字符串拼接构造 SQL 语句，未使用参数化查询。攻击者可通过 UNION SELECT 注入获取数据库中的敏感数据 |
| 教学目标 | 理解 SQL 注入原理和 UNION 注入技术，学习参数化查询和 ORM 的安全使用 |
| 触发方式 | 在订单 ID 参数中注入 `' UNION SELECT ...` 语句 |

### 2.9 V-SSTI — 服务端模板注入

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A03:2021 - Injection |
| 漏洞位置 | `app/controller/user.py` → `order_detail` 相关链路 |
| 设计原理 | 订单详情页面将用户可控数据直接传入 Jinja2 模板渲染（`render_template_string`），未做过滤。攻击者可注入模板表达式执行任意 Python 代码 |
| 教学目标 | 理解 SSTI 攻击链（从模板表达式到 RCE），学习模板沙箱和输入过滤 |
| 触发方式 | 在可控字段中注入 `{{7*7}}` 或 `{{config}}` 等 Jinja2 表达式 |

### 2.10 V-Admin-AES — 管理员 AES 密钥泄露

| 项目 | 说明 |
|---|---|
| OWASP 分类 | A02:2021 - Cryptographic Failures |
| 漏洞位置 | `app/config.py`（硬编码密钥）；`app/controller/admin.py` → `login` |
| 设计原理 | 管理员登录使用 AES 加密传输密码，但密钥和 IV 硬编码在源码和前端 JavaScript 中。攻击者可从前端代码提取密钥，解密或伪造管理员凭证 |
| 教学目标 | 理解硬编码密钥的风险，学习密钥管理（KMS）、HTTPS 传输加密和前端加密的局限性 |
| 触发方式 | 查看前端 JavaScript 源码提取 AES Key 和 IV |

## 3. 与同类平台对比

| 特性 | HackShop | DVWA | WebGoat | Pikachu |
|---|---|---|---|---|
| 业务场景 | 完整电商流程 | 独立功能页 | 课程式练习 | 独立功能页 |
| 漏洞嵌入方式 | 融入业务操作 | 独立页面 | 分课时 | 独立页面 |
| 技术栈 | Flask + MySQL + Redis | PHP + MySQL | Java + H2 | PHP + MySQL |
| 容器化部署 | Docker Compose 三服务 | Docker 单容器 | Docker 单容器 | Docker 单容器 |
| 实验重置 | 一键重置脚本 | 手动重置 | 课程内重置 | 手动重置 |
| 竞态条件漏洞 | 有 | 无 | 无 | 无 |
| SSRF 漏洞 | 有 | 无 | 有 | 有 |
| 业务逻辑漏洞 | 有（支付、兑换） | 无 | 部分 | 无 |

## 4. 文档历史
- 2026-02-22：补充文档历史章节，与其他文档格式对齐
