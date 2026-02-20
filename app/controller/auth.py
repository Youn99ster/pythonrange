from flask import Blueprint, g, jsonify, redirect, render_template, request, session, url_for

from app.models.db import User, db
from app.utils.db import redis_client
from app.utils.tools import SendResetUrl, authenticate_user, verify_email_code

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _request_data():
    # 统一读取请求参数，支持 JSON 与表单两种模式。
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form


@auth_bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id")
    g.user = db.session.get(User, user_id) if user_id is not None else None


@auth_bp.route("/user/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("auth/login.html")

    request_data = _request_data()
    email = request_data.get("email")
    password = request_data.get("password")
    remember = request_data.get("remember")
    if not email or not password:
        return jsonify({"status": "error", "message": "缺少邮箱或密码"}), 400

    payload, status = authenticate_user(email, password)
    if status != 200:
        return jsonify(payload), status

    remember_flag = str(remember).lower() in ("1", "true", "on", "yes")
    session.permanent = remember_flag
    session["user_id"] = payload["user_id"]
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

    request_data = _request_data()
    username = request_data.get("username")
    email = request_data.get("email")
    password = request_data.get("password")
    confirm_password = request_data.get("confirm_password")
    email_code = request_data.get("email_code")

    if not username or not email or not password or not confirm_password:
        return jsonify({"status": "error", "message": "缺少必填参数"}), 400
    if password != confirm_password:
        return jsonify({"status": "error", "message": "两次输入的密码不一致"}), 400
    if not verify_email_code(email, email_code):
        return jsonify({"status": "error", "message": "邮箱验证码错误"}), 400

    try:
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"注册失败：{e}"}), 500
    return jsonify({"status": "ok", "message": "注册成功"}), 200


@auth_bp.route("/user/forgot-password", methods=["GET", "POST"])
def forgot_password():
    if request.method == "GET":
        return render_template("auth/forgot-password.html", data={"page": "forgot-password page"})

    data = _request_data()
    email = data.get("email")
    if not email:
        return jsonify({"status": "error", "message": "请输入邮箱"}), 400

    user = User.query.filter_by(email=email).first()
    if not user:
        return jsonify({"status": "error", "message": "邮箱不存在"}), 404

    try:
        SendResetUrl(email, request.host, user.id)
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"发送重置邮件失败：{e}"}), 500
    return jsonify({"status": "ok", "message": "重置邮件已发送"}), 200


@auth_bp.route("/user/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):
    if request.method == "GET":
        user_id = redis_client.get(f"reset_token:{token}")
        data = {"token": token}
        if not user_id:
            data["error"] = "链接无效或已过期"
        return render_template("auth/reset-password.html", data=data)

    data = _request_data()
    password = data.get("password")
    if not password:
        return jsonify({"status": "error", "message": "请输入新密码"}), 400

    user_id = redis_client.get(f"reset_token:{token}")
    if not user_id:
        return jsonify({"status": "error", "message": "链接无效或已过期"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"status": "error", "message": "用户不存在"}), 404

    try:
        user.password = password
        db.session.commit()
        redis_client.delete(f"reset_token:{token}")
    except Exception as e:
        db.session.rollback()
        return jsonify({"status": "error", "message": f"密码重置失败：{e}"}), 500
    return jsonify({"status": "ok", "message": "密码重置成功"}), 200
