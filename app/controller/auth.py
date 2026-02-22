"""
认证蓝图（Authentication Blueprint）。

功能：
- 用户登录（邮箱 + 密码）
- 用户注册（邮箱验证码校验）
- 找回密码（发送重置链接到站内信）
- 重置密码（通过令牌验证身份）

相关漏洞：
- V-Auth-DoS：登录失败 5 次后锁定 5 分钟（Redis 计数），可被利用锁定任意账号
- V-Host-Inject：密码重置链接直接使用请求 Host 头拼接，可被篡改指向恶意域名

before_app_request 钩子：
  每次请求前根据 session['user_id'] 从数据库加载用户对象到 g.user，
  供其他蓝图和模板直接使用。
"""

import logging

from flask import Blueprint, g, jsonify, redirect, render_template, request, session, url_for

from app.models.db import User, db
from app.utils.db import redis_client
from app.utils.tools import authenticate_user, request_data, safe_commit, send_reset_url, verify_email_code

# 认证蓝图：登录、注册、找回密码与重置密码流程。
auth_bp = Blueprint("auth", __name__, url_prefix="/auth")
logger = logging.getLogger(__name__)


@auth_bp.before_app_request
def load_logged_in_user():
    # 将当前登录用户写入 g.user，供其他路由直接读取。
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id is not None else None


@auth_bp.route("/user/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    data = request_data()
    email = data.get("email")
    password = data.get("password")
    remember = data.get("remember")
    if not email or not password:
        return jsonify({"status": "error", "message": "缺少邮箱或密码"}), 400

    payload, status = authenticate_user(email, password)
    if status != 200:
        return jsonify(payload), status

    session.permanent = str(remember).lower() in ("1", "true", "on", "yes")
    session["user_id"] = payload["user_id"]
    # Ajax 登录返回 JSON，普通表单登录走重定向。
    if request.is_json or request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"status": "ok", "message": "登录成功"}), 200
    return redirect(url_for("main.index"))


@auth_bp.route("/user/logout")
def logout():
    session.clear()
    return redirect(url_for("main.index"))


@auth_bp.route("/user/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("auth/register.html", data={"page": "register page"})

    data = request_data()
    username = data.get("username")
    email = data.get("email")
    password = data.get("password")
    confirm_password = data.get("confirm_password")
    email_code = data.get("email_code")

    if not username or not email or not password or not confirm_password:
        return jsonify({"status": "error", "message": "缺少必填参数"}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "两次输入的密码不一致"}), 400
    if not verify_email_code(email, email_code):
        return jsonify({"status": "error", "message": "邮箱验证码错误"}), 400

    # 靶场场景保留明文密码逻辑，便于演示认证风险。
    db.session.add(User(username=username, email=email, password=password))
    err = safe_commit("register commit failed", (jsonify({"status": "error", "message": "注册失败，请稍后重试"}), 500))
    if err:
        return err
    return jsonify({"status": "ok", "message": "注册成功"}), 200


@auth_bp.route("/user/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot-password.html", data={"page": "forgot-password page"})

    data = request_data()
    email = data.get("email")
    if not email:
        return jsonify({"status": "error", "message": "请输入邮箱"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"status": "error", "message": "邮箱不存在"}), 404

    try:
        send_reset_url(email, request.host, user.id)
    except Exception:
        db.session.rollback()
        logger.exception("send reset url failed")
        return jsonify({"status": "error", "message": "发送重置邮件失败，请稍后重试"}), 500
    return jsonify({"status": "ok", "message": "重置邮件已发送"}), 200


@auth_bp.route("/user/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "GET":
        user_id = redis_client.get(f"reset_token:{token}")
        data = {"token": token}
        if not user_id:
            data["error"] = "链接无效或已过期"
        return render_template("auth/reset-password.html", data=data)

    data = request_data()
    password = data.get("password")
    if not password:
        return jsonify({"status": "error", "message": "请输入新密码"}), 400

    user_id = redis_client.get(f"reset_token:{token}")
    if not user_id:
        return jsonify({"status": "error", "message": "链接无效或已过期"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 404

    user.password = password
    err = safe_commit("reset_password commit failed", (jsonify({"status": "error", "message": "密码重置失败，请稍后重试"}), 500))
    if err:
        return err
    redis_client.delete(f"reset_token:{token}")
    return jsonify({"status": "ok", "message": "密码重置成功"}), 200
