"""
靶场重置脚本。

执行流程：
  1. 删除并重建所有数据库表（drop_all + create_all）
  2. 清空 Redis 缓存（flushdb）
  3. 重新执行 seed 脚本插入默认数据

用法：
  python scripts/reset_lab.py
  docker compose exec web python scripts/reset_lab.py
  RESET_LAB_ON_BOOT=1 时容器启动自动执行
"""

import os
import sys

# 确保从项目根目录导入 app 包
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app
from app.models.db import db
from app.utils.db import redis_client
from scripts.seed import seed


def reset():
    """重置数据库和缓存，然后重新播种初始数据。"""
    with app.app_context():
        # 第一步：销毁并重建所有表结构
        db.drop_all()
        db.create_all()
        db.session.commit()
        print("Database reset complete")

        # 第二步：清空 Redis 中的所有键（验证码、锁定计数等）
        redis_client.flushdb()
        print("Redis cache cleared")

    # 第三步：重新插入种子数据
    seed()


if __name__ == "__main__":
    reset()
