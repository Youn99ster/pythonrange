"""
数据库索引补全脚本。

在容器启动时（start.sh）自动执行，为高频查询字段创建索引。
采用幂等逻辑：先查 information_schema 判断索引是否存在，不存在才创建。
直接使用 pymysql 而非 ORM，避免依赖 Flask 应用上下文。
"""

import os
from contextlib import closing

import pymysql


def _connect():
    """创建到 MySQL 的原生连接（autocommit=True，DDL 立即生效）。"""
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "hackshop_user"),
        password=os.getenv("MYSQL_PASSWORD", "hackshop_password"),
        db=os.getenv("MYSQL_DB", "hackshop_db"),
        charset="utf8mb4",
        autocommit=True,
    )


# 索引定义列表：(表名, 索引名, CREATE INDEX DDL)
INDEXES = [
    ("mail_logs", "idx_mail_logs_created_at", "CREATE INDEX idx_mail_logs_created_at ON mail_logs (created_at)"),
    ("mail_logs", "idx_mail_logs_receiver", "CREATE INDEX idx_mail_logs_receiver ON mail_logs (receiver)"),
    ("goods", "idx_goods_status", "CREATE INDEX idx_goods_status ON goods (status)"),
    ("goods", "idx_goods_category", "CREATE INDEX idx_goods_category ON goods (category)"),
    ("goods", "idx_goods_price", "CREATE INDEX idx_goods_price ON goods (price)"),
    ("cart_items", "idx_cart_items_user_id", "CREATE INDEX idx_cart_items_user_id ON cart_items (user_id)"),
    ("cart_items", "idx_cart_items_goods_id", "CREATE INDEX idx_cart_items_goods_id ON cart_items (goods_id)"),
    ("cart_items", "idx_cart_items_user_goods", "CREATE INDEX idx_cart_items_user_goods ON cart_items (user_id, goods_id)"),
    ("`order`", "idx_order_user_id", "CREATE INDEX idx_order_user_id ON `order` (user_id)"),
    ("`order`", "idx_order_generatetime", "CREATE INDEX idx_order_generatetime ON `order` (generatetime)"),
    ("`order`", "idx_order_payment_status", "CREATE INDEX idx_order_payment_status ON `order` (payment_status)"),
    ("order_items", "idx_order_items_order_id", "CREATE INDEX idx_order_items_order_id ON order_items (order_id)"),
    ("order_items", "idx_order_items_goods_id", "CREATE INDEX idx_order_items_goods_id ON order_items (goods_id)"),
    ("address", "idx_address_user_id", "CREATE INDEX idx_address_user_id ON address (user_id)"),
    ("voucher", "idx_voucher_status", "CREATE INDEX idx_voucher_status ON voucher (status)"),
    ("voucher", "idx_voucher_used_by", "CREATE INDEX idx_voucher_used_by ON voucher (used_by)"),
]


def _index_exists(cur, schema: str, table: str, index_name: str) -> bool:
    """通过 information_schema 检查指定索引是否已存在。"""
    raw_table = table.strip("`")
    cur.execute(
        """
        SELECT 1
        FROM information_schema.statistics
        WHERE table_schema = %s
          AND table_name = %s
          AND index_name = %s
        LIMIT 1
        """,
        (schema, raw_table, index_name),
    )
    return cur.fetchone() is not None


def ensure_indexes() -> None:
    """遍历 INDEXES 列表，跳过已存在的索引，创建缺失的索引。"""
    schema = os.getenv("MYSQL_DB", "hackshop_db")
    with closing(_connect()) as conn, closing(conn.cursor()) as cur:
        for table, index_name, ddl in INDEXES:
            if _index_exists(cur, schema, table, index_name):
                print(f"skip {index_name}")
                continue
            cur.execute(ddl)
            print(f"create {index_name}")


if __name__ == "__main__":
    ensure_indexes()
