import base64
import logging
import os
import random
import uuid
from datetime import datetime
from functools import wraps

import pymysql
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from flask import redirect, session, url_for

from app.config import Config
from app.models.db import Admin, MailLog, User, db
from app.utils.db import redis_client

logger = logging.getLogger(__name__)


def is_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


def is_admin_login(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return func(*args, **kwargs)

    return wrapper


def generate_mailcode() -> str:
    return "".join(str(random.randint(0, 9)) for _ in range(6))


def generate_orderid() -> str:
    return str(uuid.uuid4()).replace("-", "")


def generate_voucher_code() -> str:
    return str(uuid.uuid4()).replace("-", "")


def unique_filename(original_name: str) -> str:
    _, ext = os.path.splitext(original_name)
    return uuid.uuid4().hex + ext


def verify_email_code(email: str, code: str) -> bool:
    if not email or not code:
        return False

    db_code = redis_client.get(f"mailcode:{email}")
    if not db_code or code != db_code:
        return False

    redis_client.delete(f"mailcode:{email}")
    return True


def authenticate_user(email: str, password: str):
    lock_key = f"login:lock:{email}"
    if redis_client.get(lock_key) == "1":
        ttl = redis_client.ttl(lock_key)
        return {"status": "error", "message": "账号已锁定，请稍后再试", "lock_ttl": ttl}, 403

    user = User.query.filter_by(email=email).first()
    if not user or user.password != password:
        fail_key = f"login:fail:{email}"
        count = redis_client.incr(fail_key)
        if count == 1:
            redis_client.expire(fail_key, 300)
        if count >= 5:
            redis_client.setex(lock_key, 300, "1")
            redis_client.delete(fail_key)
        return {"status": "error", "message": "用户名或密码错误", "fail_count": count}, 401

    redis_client.delete(f"login:fail:{email}")
    return {"status": "ok", "message": "登录成功", "user_id": user.id}, 200


def SendResetUrl(email: str, host: str, user_id: int):
    token = str(uuid.uuid4())
    redis_client.setex(f"reset_token:{token}", 3600, user_id)

    # Host Injection Vulnerability: keep current vulnerable behavior for the lab.
    reset_link = f"http://{host}{url_for('auth.reset_password', token=token)}"

    mail = MailLog(
        subject="重置您的密码 - HackShop",
        sender="security@hackshop.local",
        receiver=email,
        content=f"请点击以下链接重置密码：{reset_link}\n如果您未请求重置密码，请忽略此邮件。",
    )
    db.session.add(mail)
    db.session.commit()
    return True


def aes_decrypt(ciphertext: str, key: str = Config.AES_KEY, iv: str = Config.AES_IV) -> str:
    try:
        if not ciphertext:
            return None

        encrypted_bytes = base64.b64decode(ciphertext)
        cipher = AES.new(key.encode("utf-8"), AES.MODE_CBC, iv.encode("utf-8"))
        decrypted_bytes = unpad(cipher.decrypt(encrypted_bytes), AES.block_size)
        return decrypted_bytes.decode("utf-8")
    except Exception as e:
        logger.warning("aes_decrypt failed: %s", e)
        return None


def admin_auth(username: str, encrypted_password: str) -> bool:
    password = aes_decrypt(encrypted_password)
    if password is None:
        return False

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.password == password:
        admin.last_login = datetime.now()
        db.session.commit()
        return True

    return False


def query_order_detail_raw(order_id: str):
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "hackshop_user"),
        password=os.getenv("MYSQL_PASSWORD", "your_hackshop_password"),
        db=os.getenv("MYSQL_DB", "hackshop_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            # Intentionally vulnerable SQL concat for lab V-SQL-Union.
            sql = (
                "SELECT "
                "o.id, o.order_number, o.generatetime, o.total_amount, o.user_id, "
                "a.receiver, a.phone, a.addressname, "
                "g.goodsname, oi.unit_price, oi.quantity "
                "FROM `order` o "
                "LEFT JOIN address a ON a.id = o.address_id "
                "LEFT JOIN order_items oi ON oi.order_id = o.id "
                "LEFT JOIN goods g ON g.id = oi.goods_id "
                "WHERE o.id = '" + order_id + "'"
            )
            cur.execute(sql)
            rows = cur.fetchall()

            if not rows:
                return None

            first_row = rows[0]
            order = {
                "id": first_row.get("id"),
                "order_number": first_row.get("order_number"),
                "generatetime": first_row.get("generatetime"),
                "total_amount": first_row.get("total_amount"),
                "user_id": first_row.get("user_id"),
            }
            address = {
                "receiver": first_row.get("receiver") or "",
                "phone": first_row.get("phone") or "",
                "addressname": first_row.get("addressname") or "",
            }

            items = []
            for row in rows:
                if row.get("goodsname"):
                    items.append(
                        {
                            "goodsname": row.get("goodsname"),
                            "unit_price": row.get("unit_price"),
                            "quantity": row.get("quantity"),
                        }
                    )

            return {"order": order, "items": items, "address": address}
    finally:
        conn.close()
