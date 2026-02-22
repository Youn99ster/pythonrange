"""
HackShop 通用工具函数模块。

包含：
- 鉴权装饰器：is_login（前台用户）、is_admin_login（管理员）
- 验证码：generate_mailcode / verify_email_code（Redis 存储）
- ID 生成：generate_uuid_hex / unique_filename
- 请求解析：request_data（兼容 JSON / form）
- DB 提交：safe_commit（统一事务提交与异常处理）
- 订单状态映射：get_order_status_meta
- 认证逻辑：authenticate_user（含 Redis 防爆破）、admin_auth（AES 解密）
- 密码重置：send_reset_url（V-Host-Inject 漏洞保留）
- AES 解密：aes_decrypt（V-Admin-AES 漏洞配套）
- 原生 SQL 查询：query_order_detail_raw（V-SQL-Union 漏洞保留）
"""

import base64
import logging
import os
import secrets
import uuid
from datetime import datetime
from functools import wraps

import pymysql
from Crypto.Cipher import AES
from Crypto.Util.Padding import unpad
from flask import g, jsonify, redirect, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.config import Config
from app.models.db import Admin, MailLog, User, db
from app.utils.db import redis_client

logger = logging.getLogger(__name__)

# 订单状态 → (前端显示文案, CSS 样式标识) 的映射表
ORDER_STATUS_META = {
    "pending": ("待付款", "pending"),
    "paid": ("已支付", "active"),
    "shipped": ("已发货", "pending"),
    "completed": ("已完成", "active"),
    "cancelled": ("已取消", "inactive"),
}


def get_order_status_meta(status: str):
    # 统一订单状态到前端展示文案和样式标识的映射。
    return ORDER_STATUS_META.get(status or "pending", ORDER_STATUS_META["pending"])


def is_login(func):
    """前台用户登录校验装饰器，未登录时重定向到登录页。"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        # 未登录时清理残留会话，避免脏 session 干扰后续流程。
        if not session.get("user_id") or getattr(g, "user", None) is None:
            session.clear()
            return redirect(url_for("auth.login"))
        return func(*args, **kwargs)

    return wrapper


def is_admin_login(func):
    """管理员登录校验装饰器，未登录时重定向到管理后台登录页。"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin.login"))
        return func(*args, **kwargs)

    return wrapper


def generate_mailcode() -> str:
    """生成 6 位随机数字验证码（密码学安全）。"""
    return "".join(str(secrets.randbelow(10)) for _ in range(6))


def generate_uuid_hex() -> str:
    """生成 32 位无横线 UUID，用于订单主键、储值券兑换码等场景。"""
    return uuid.uuid4().hex


def unique_filename(original_name: str) -> str:
    """基于 UUID 生成唯一文件名，保留原始扩展名。"""
    _, ext = os.path.splitext(original_name)
    return uuid.uuid4().hex + ext


def request_data():
    """统一读取请求参数，兼容 JSON 与表单两种提交格式。"""
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form


def safe_commit(error_log: str, error_response=None):
    """
    统一 DB 提交 + 异常处理。
    成功返回 None，失败回滚并返回 error_response（默认 JSON 500）。
    """
    try:
        db.session.commit()
        return None
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(error_log)
        if error_response is not None:
            return error_response
        return jsonify({"error": "操作失败，请稍后重试"}), 500


def verify_email_code(email: str, code: str) -> bool:
    """校验邮箱验证码，验证成功后立即销毁，防止重复使用。"""
    # 验证成功后立即销毁验证码，避免重复使用。
    if not email or not code:
        return False

    db_code = redis_client.get(f"mailcode:{email}")
    if not db_code or code != db_code:
        return False

    redis_client.delete(f"mailcode:{email}")
    return True


def authenticate_user(email: str, password: str):
    """
    前台用户登录认证。
    基于 Redis 的防爆破机制：5 次失败后锁定 5 分钟（V-Auth-DoS 漏洞场景）。
    """
    # 基于 Redis 的简单防爆破：失败计数 + 临时锁定。
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


def send_reset_url(email: str, host: str, user_id: int):
    """
    生成密码重置链接并写入站内信。
    V-Host-Inject 漏洞：直接使用请求中的 Host 头拼接链接，未做白名单校验。
    """
    token = str(uuid.uuid4())
    redis_client.setex(f"reset_token:{token}", 3600, user_id)

    # Host Injection 漏洞保留：为靶场演示不做 host 白名单校验。
    reset_link = f"http://{host}{url_for('auth.reset_password', token=token)}"

    mail = MailLog(
        subject="重置您的密码 - HackShop",
        sender="security@hackshop.local",
        receiver=email,
        content=f"请点击以下链接重置密码：{reset_link}\n如果您未请求重置密码，请忽略此邮件。",
    )
    try:
        db.session.add(mail)
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("send_reset_url commit failed")
        raise
    return True


def aes_decrypt(ciphertext: str, key: str = Config.AES_KEY, iv: str = Config.AES_IV) -> str:
    """AES-CBC 解密（V-Admin-AES 漏洞配套），解密失败返回 None。"""
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
    """
    管理员登录认证。
    前端 AES 加密密码 → 服务端解密 → 明文比对（V-Admin-AES 漏洞流程）。
    """
    # 管理员登录采用前端 AES 密文 + 服务端解密的靶场流程。
    password = aes_decrypt(encrypted_password)
    if password is None:
        return False

    admin = Admin.query.filter_by(username=username).first()
    if admin and admin.password == password:
        admin.last_login = datetime.now()
        try:
            db.session.commit()
            return True
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("admin_auth commit failed")
            return False

    return False


def query_order_detail_raw(order_id: str):
    """
    使用原生 SQL 查询订单详情（绕过 ORM）。
    V-SQL-Union 漏洞：order_id 直接拼接到 SQL 语句中，未使用参数化查询，
    攻击者可通过 UNION SELECT 注入获取任意数据。
    """
    conn = pymysql.connect(
        host=os.getenv("MYSQL_HOST", "127.0.0.1"),
        port=int(os.getenv("MYSQL_PORT", "3306")),
        user=os.getenv("MYSQL_USER", "hackshop_user"),
        password=os.getenv("MYSQL_PASSWORD", "hackshop_password"),
        db=os.getenv("MYSQL_DB", "hackshop_db"),
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
    )
    try:
        with conn.cursor() as cur:
            # SQL 注入漏洞保留：故意拼接 SQL 用于 V-SQL-Union 场景。
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
