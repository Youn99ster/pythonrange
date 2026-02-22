"""
数据库初始种子脚本。

幂等执行：仅在对应表为空时插入默认数据。
默认种子账号：
  - 管理员: admin / admin123
  - 普通用户: alice@test.com / alice123（余额 9999）
  - 演示商品: Demo Product

用法：
  python scripts/seed.py          # 本地
  docker compose exec web python scripts/seed.py  # 容器内
"""

import os
import sys
from datetime import datetime

# 确保从项目根目录导入 app 包，无论在哪个目录执行
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from app import app
from app.models.db import db, Admin, User, Goods


def seed():
    """向空表中插入默认管理员、用户和演示商品。"""
    with app.app_context():
        # 管理员账号（仅在无管理员时创建）
        if not Admin.query.first():
            db.session.add(Admin(username="admin", password="admin123"))

        # 演示用户（仅在无用户时创建）
        if not User.query.first():
            db.session.add(User(username="alice", email="alice@test.com", password="alice123", balance=9999))

        # 演示商品（仅在无商品时创建）
        if not Goods.query.first():
            db.session.add(Goods(goodsname="Demo Product", category="lab", price=99.9, stock=100, status="0",
                                mainimg="/static/img/default.jpg", content="seed demo"))

        db.session.commit()
        print("Seed complete: admin/admin123, alice@test.com/alice123")

if __name__ == "__main__":
    seed()
