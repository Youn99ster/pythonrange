#!/bin/sh
# ============================================================
# HackShop 容器启动入口脚本
#
# 执行流程：
#   1. 等待 MySQL 就绪（最多 90 秒轮询）
#   2. 执行数据库迁移（有 migrations 目录）或直接建表
#   3. 可选：RESET_LAB_ON_BOOT=1 重置数据库 + 缓存
#   4. 可选：SEED_ON_BOOT=1 播种初始数据
#   5. 补全数据库索引
#   6. 启动 Gunicorn WSGI 服务器
# ============================================================
set -eu

# ---- 第一步：等待 MySQL 可连接 ----
python - <<'PY'
import os, time
import pymysql

host = os.getenv("MYSQL_HOST", "mysql")
port = int(os.getenv("MYSQL_PORT", "3306"))
user = os.getenv("MYSQL_USER", "hackshop_user")
password = os.getenv("MYSQL_PASSWORD", "hackshop_password")
db = os.getenv("MYSQL_DB", "hackshop_db")

for _ in range(90):
    try:
        conn = pymysql.connect(host=host, port=port, user=user, password=password, database=db, connect_timeout=2)
        conn.close()
        break
    except Exception:
        time.sleep(1)
else:
    raise SystemExit("MySQL not ready")
PY


# ---- 第二步：数据库迁移或建表 ----
if [ -d "migrations" ]; then
  flask --app app db upgrade
else
  python - <<'PY'
from app import app
from app.models.db import db

with app.app_context():
    db.create_all()
PY
fi

# ---- 第三步：可选的靶场重置 ----
if [ "${RESET_LAB_ON_BOOT:-0}" = "1" ]; then
  echo "RESET_LAB_ON_BOOT: resetting database and cache..."
  python scripts/reset_lab.py
fi

# ---- 第四步：可选的数据播种 ----
if [ "${SEED_ON_BOOT:-0}" = "1" ]; then
  echo "SEED_ON_BOOT: seeding initial data..."
  python scripts/seed.py
fi

# ---- 第五步：补全数据库索引（幂等） ----
python scripts/ensure_indexes.py || true

# ---- 第六步：启动 Gunicorn（gthread 模式） ----
WEB_WORKERS="${WEB_WORKERS:-4}"
WEB_THREADS="${WEB_THREADS:-4}"
WEB_TIMEOUT="${WEB_TIMEOUT:-120}"

exec gunicorn -w "${WEB_WORKERS}" -k gthread --threads "${WEB_THREADS}" -t "${WEB_TIMEOUT}" -b 0.0.0.0:8000 app:app
