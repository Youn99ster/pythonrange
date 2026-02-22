"""
用户中心蓝图（User Center Blueprint）。

功能：
- 余额查询（/user/balance）
- 收货地址增删改查（CRUD）
- 储值券兑换（/user/redeem）
- 个人中心页面（信息 / 订单 / 地址 / 资产 四个标签页）
- 订单详情查看（/user/order/<id>）

相关漏洞：
- V-IDOR-Modify：编辑/删除地址时未校验归属关系，可越权操作他人地址
- V-SQL-Union：订单详情使用原生 SQL 拼接 order_id，存在 SQL 注入
- V-SSTI：订单详情通过 render_template_string 渲染用户输入，存在服务端模板注入
"""

import logging
from datetime import datetime

from flask import Blueprint, flash, jsonify, redirect, render_template, render_template_string, request, session, url_for
from sqlalchemy.exc import SQLAlchemyError

from app.models.db import Address, Order, User, Voucher, db, VOUCHER_UNUSED, VOUCHER_USED
from app.utils.tools import get_order_status_meta, is_login, query_order_detail_raw

# 用户中心蓝图：地址、资产、订单与代金券能力。
user_bp = Blueprint("user", __name__, url_prefix="/user")
logger = logging.getLogger(__name__)


def _commit_or_flash(success_msg: str, error_log: str):
    """统一 DB 提交 + flash 提示，减少重复 try/except 样板代码。"""
    try:
        db.session.commit()
        flash(success_msg, "success")
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception(error_log)
        flash("操作失败，请稍后重试", "danger")


_PROFILE_ENDPOINT = "user.profile"


@user_bp.route("/balance", methods=["GET"])
@is_login
def get_balance():
    user = db.session.get(User, session.get("user_id"))
    if not user:
        return jsonify({"error": "用户不存在"}), 404
    return jsonify({"balance": user.balance if user.balance else 0.00})


@user_bp.route("/address/list", methods=["GET"])
@is_login
def address_list():
    # 仅返回前端结算页所需字段，避免暴露无关信息。
    addresses = Address.query.filter_by(user_id=session.get("user_id")).all()
    return jsonify(
        [
            {
                "id": addr.id,
                "receiver": addr.receiver,
                "phone": addr.phone,
                "addressname": addr.addressname,
            }
            for addr in addresses
        ]
    )


@user_bp.route("/voucher/redeem", methods=["POST"])
@is_login
def voucher_redeem():
    # 代金券兑换流程：校验状态 -> 入账 -> 标记已使用。
    user_id = session.get("user_id")
    code = request.form.get("code") or request.args.get("code")
    if not code:
        return jsonify({"error": "缺少兑换码"}), 400

    voucher = Voucher.query.filter_by(code=code).first()
    if not voucher:
        return jsonify({"error": "兑换码不存在"}), 404
    if voucher.status != VOUCHER_UNUSED:
        return jsonify({"error": "兑换码已使用或不可用"}), 409
    if voucher.expires_at and voucher.expires_at < datetime.now():
        return jsonify({"error": "兑换码已过期"}), 400

    user = db.session.get(User, user_id)
    if not user:
        return jsonify({"error": "用户不存在"}), 404

    voucher.status = VOUCHER_USED
    voucher.used_by = user.id
    voucher.used_at = datetime.now()
    user.balance = (user.balance or 0.0) + voucher.amount

    try:
        db.session.commit()
        refreshed = db.session.get(User, user_id)
        return jsonify(
            {
                "message": "兑换成功",
                "code": code,
                "amount": voucher.amount,
                "balance": refreshed.balance,
            }
        ), 200
    except SQLAlchemyError:
        db.session.rollback()
        logger.exception("voucher_redeem commit failed")
        return jsonify({"error": "兑换失败，请稍后重试"}), 500


@user_bp.route("/address/add", methods=["POST"])
@is_login
def add_address():
    user_id = session.get("user_id")
    receiver = request.form.get("receiver")
    phone = request.form.get("phone")
    addressname = request.form.get("addressname")

    if receiver and phone and addressname:
        db.session.add(Address(user_id=user_id, receiver=receiver, phone=phone, addressname=addressname))
        _commit_or_flash("地址添加成功", "add_address commit failed")
    return redirect(url_for(_PROFILE_ENDPOINT, section="address"))


@user_bp.route("/address/edit/<int:address_id>", methods=["POST"])
@is_login
def edit_address(address_id):
    address = db.session.get(Address, address_id)
    # IDOR Vulnerability: We are NOT checking if address.user_id == user_id
    # This allows users to edit other people's addresses if they know the ID
    if address:
        address.receiver = request.form.get("receiver")
        address.phone = request.form.get("phone")
        address.addressname = request.form.get("addressname")
        _commit_or_flash("地址更新成功", "edit_address commit failed")
    return redirect(url_for(_PROFILE_ENDPOINT, section="address"))


@user_bp.route("/address/delete/<int:address_id>", methods=["POST"])
@is_login
def delete_address(address_id):
    address = db.session.get(Address, address_id)
    # IDOR Vulnerability: No ownership check
    if address:
        db.session.delete(address)
        _commit_or_flash("地址删除成功", "delete_address commit failed")
    return redirect(url_for(_PROFILE_ENDPOINT, section="address"))


def _load_section_data(section: str, user_id: int, user) -> dict:
    """按标签页懒加载个人中心数据，避免一次请求拉取全部信息。"""
    data = {"page": "profile", "section": section}
    if section == "orders":
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.generatetime.desc()).all()
        data["orders"] = [
            {
                "id": order.id,
                "display_id": order.order_number,
                "date": order.generatetime.strftime("%Y-%m-%d") if order.generatetime else "",
                "total": order.total_amount,
                "status_label": get_order_status_meta(order.payment_status)[0],
                "status_class": get_order_status_meta(order.payment_status)[1],
            }
            for order in orders
        ]
    elif section == "address":
        addresses = Address.query.filter_by(user_id=user_id).all()
        data["addresses"] = [
            {"id": addr.id, "receiver": addr.receiver, "phone": addr.phone, "addressname": addr.addressname}
            for addr in addresses
        ]
    elif section == "assets":
        data["assets"] = {"balance": user.balance or 0.00, "points": 0}
    elif section == "info":
        data["info"] = {"username": user.username, "email": user.email}
    return data


@user_bp.route("/profile", methods=["GET", "POST"])
@is_login
def profile():
    user_id = session.get("user_id")
    user = db.session.get(User, user_id)
    if not user:
        return redirect(url_for("auth.login"))

    section = request.args.get("section", "orders")
    if request.method == "POST" and section == "info":
        new_username = request.form.get("username", "").strip()
        new_password = request.form.get("password", "").strip()
        if new_username:
            user.username = new_username
        if new_password:
            user.password = new_password
        if new_username or new_password:
            _commit_or_flash("个人信息更新成功", "profile update commit failed")
        return redirect(url_for(_PROFILE_ENDPOINT, section="info"))

    return render_template("user/profile.html", data=_load_section_data(section, user_id, user))


@user_bp.route("/order/<order_id>", methods=["GET"])
@is_login
def order_detail(order_id):
    # 订单详情故意走原生 SQL 查询函数，用于靶场漏洞演示。
    raw = query_order_detail_raw(order_id)
    if not raw:
        return "订单不存在", 404

    shipping_info = ""
    if raw.get("address"):
        address = raw["address"]
        shipping_info = f"{address.get('receiver', '')}, {address.get('phone', '')}, {address.get('addressname', '')}"

    products = [
        {
            "name": item.get("goodsname") or "Unknown",
            "price": item.get("unit_price"),
            "quantity": item.get("quantity"),
        }
        for item in raw.get("items", [])
    ]

    order_raw = raw["order"]
    date_val = order_raw.get("generatetime")
    if isinstance(date_val, datetime):
        date_str = date_val.strftime("%Y-%m-%d")
    elif date_val is not None:
        date_str = str(date_val)
    else:
        date_str = ""

    order_data = {
        "id": order_raw.get("order_number"),
        "products": products,
        "total": order_raw.get("total_amount"),
        "date": date_str,
        "shipping_info": shipping_info,
    }

    # V-SSTI: 服务端模板注入（保留用于靶场）。
    # 漏洞原因：在渲染模板前，先把用户输入拼接到模板字符串中。
    username = request.args.get("username")
    if not username:
        user_id = session.get("user_id")
        user = db.session.get(User, user_id) if user_id else None
        if user:
            username = user.username
    if not username:
        username = "HackShop 用户"

    # 漏洞代码：将用户输入直接拼接进模板字符串。
    template_str = f"""
    <div class="modal-header">
        <h5 class="modal-title">订单详情 - {username}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="关闭"></button>
    </div>
    <div class="modal-body">
        <p><strong>订单号:</strong> {order_data['id']}</p>
        <p><strong>下单时间:</strong> {order_data['date']}</p>
        <hr>
        <h6>商品列表:</h6>
        <ul>
            {{% for item in order.products %}}
            <li>{{{{ item.name }}}} - ¥{{{{ item.price }}}} x {{{{ item.quantity }}}}</li>
            {{% endfor %}}
        </ul>
        <hr>
        <p class="text-end"><strong>总计: ¥{{{{ order.total }}}}</strong></p>
        <p><strong>收货信息:</strong> {order_data['shipping_info']}</p>
    </div>
    <div class="modal-footer">
        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">关闭</button>
    </div>
    """
    return render_template_string(template_str, order=order_data)
