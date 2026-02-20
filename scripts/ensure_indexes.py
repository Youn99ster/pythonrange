import os
from contextlib import closing

import pymysql


def _connect():
    return pymysql.connect(
        host=os.getenv("MYSQL_HOST", "mysql"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "hackshop_user"),
        password=os.getenv("MYSQL_PASSWORD", "hackshop_password"),
        db=os.getenv("MYSQL_DB", "hackshop_db"),
        charset="utf8mb4",
        autocommit=True,
    )


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
