# pythonrange

pythonrange 是一个以仿真电商业务为核心的 Web 安全教学靶场。

项目目标不是“漏洞题列表”，而是在真实业务流（注册、下单、支付、后台管理）中完成漏洞发现与利用。

## 技术栈
- Backend: Flask + SQLAlchemy + Flask-Migrate
- Database: MySQL 8.0
- Cache: Redis 6
- Frontend: Jinja2 + Bootstrap 5 + JavaScript
- Runtime: Gunicorn
- Deployment: Docker Compose

## 核心模块
- 用户认证：注册、登录、找回密码、重置密码
- 商城流程：商品浏览、购物车、下单、支付、订单详情
- 用户中心：地址管理、余额、储值券兑换
- 管理后台：商品/订单/用户/储值券管理、批量导入
- 仿真工具：模拟收件箱、初始化页面 `/setup`

## 漏洞场景（10个）
- V-Auth-DoS
- V-Host-Inject
- V-CSRF-Pay
- V-Race-Condition
- V-IDOR-View
- V-IDOR-Modify
- V-SSRF
- V-SQL-Union
- V-SSTI
- V-Admin-AES

## 使用方式（仅容器）

### 1. 启动（推荐完整重置）
```bash
docker compose down -v
docker compose up -d --build
```

### 2. 检查状态
```bash
docker compose ps
docker compose logs -f web
```

### 3. 访问入口
- 前台首页：`http://127.0.0.1:8000/`
- 初始化：`http://127.0.0.1:8000/setup`
- 后台登录：`http://127.0.0.1:8000/admin/login`

### 4. 初始化数据
首次启动访问 `/setup`：
- 创建/更新管理员账号
- 导入 `product.json` 商品数据

## 容器内维护命令

### 1. 重置实验环境（清库 + 重新种子）
```bash
docker compose exec web python scripts/reset_lab.py
```

### 2. 仅执行种子数据
```bash
docker compose exec web python scripts/seed.py
```

### 3. 查看 Flask 路由
```bash
docker compose exec web flask --app app routes
```

### 4. 手动执行迁移
```bash
docker compose exec web flask --app app db upgrade
```

### 5. 容器启动自动执行（可选）
在 `docker-compose.yml` 的 `web.environment` 添加：
- `SEED_ON_BOOT=1`
- `RESET_LAB_ON_BOOT=1`

## 项目结构（核心）
```text
app/
  controller/      # main/auth/order/user/admin
  models/          # SQLAlchemy 数据模型
  template/        # Jinja2 页面
  static/          # 静态资源
  utils/           # Redis、工具函数、日志配置
scripts/
  seed.py
  reset_lab.py
docs/
  PRD.md
  tech-spec.md
  ui-ux.md
start.sh
docker-compose.yml
Dockerfile
```

## 运行口径
- 官方支持与验收路径：仅 Docker Compose。
- 本地 Python 直接运行仅用于开发调试，不作为靶场交付与验收方式。

## 注意事项
- 本项目包含“有意设计”的漏洞，仅用于授权教学与研究环境。
- 当前默认配置面向开发/教学，不是生产安全基线。
- 非安全质量治理应遵循“不破坏漏洞教学链路”的原则。
