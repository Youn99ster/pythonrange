import logging
from datetime import datetime
from uuid import uuid4

from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, url_for
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import joinedload

from app.models.db import CartItem, Goods, Order, OrderItem, db
from app.utils.tools import generate_orderid, is_login


# 订单蓝图：购物车、创建订单与支付流程。
order_bp = Blueprint("order", __name__, url_prefix="/order")
logger = logging.getLogger(__name__)


def _json_data():
    # 购物车接口统一使用 JSON，读取失败时返回空对象避免 500。
    return request.get_json(silent=True) or {}


def _parse_positive_int(raw, default=1):
    # 统一处理数量参数，兜底为正整数。
    try:
        value = int(raw)
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


def _generate_order_number(user_id: int) -> str:
    # 避免同一用户同一秒多次下单导致 order_number 唯一键冲突。
    return f"{datetime.now():%Y%m%d%H%M%S%f}{int(user_id):04d}{uuid4().hex[:6]}"


def _auth_required_json():
    # 购物车相关接口统一使用 JSON 的未登录响应。
    if not g.user:
        return (
            jsonify({"success": False, "message": "请先登录", "redirect": url_for("auth.login")}),
            401,
        )
    return None


def _json_db_error(log_key: str, message: str):
    # 所有数据库异常统一回滚并记录日志，避免会话脏状态污染后续请求。
    db.session.rollback()
    logger.exception(log_key)
    return jsonify({"success": False, "message": message}), 500


@order_bp.app_context_processor
def inject_cart_count():
    # 将购物车数量注入模板，减少页面重复查询逻辑。
    if hasattr(g, "user") and g.user:
        try:
            return dict(cart_count=CartItem.query.filter_by(user_id=g.user.id).count())
        except SQLAlchemyError:
            logger.exception("inject_cart_count failed")
    return dict(cart_count=0)


@order_bp.route("/cart")
def cart():
    if not g.user:
        return redirect(url_for("auth.login"))
    cart_items = CartItem.query.options(joinedload(CartItem.goods)).filter_by(user_id=g.user.id).all()
    items_data = []
    for item in cart_items:
        if not item.goods:
            continue
        items_data.append(
            {
                "id": item.id,
                "goods": {
                    "id": item.goods.id,
                    "goodsname": item.goods.goodsname,
                    "model": item.goods.model,
                    "price": item.goods.price,
                    "mainimg": item.goods.mainimg,
                },
                "quantity": item.quantity,
                "selected": True,
            }
        )
    return render_template("order/cart.html", cart_items_json=items_data)


@order_bp.route("/cart/add", methods=["POST"])
def add_to_cart():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    data = _json_data()
    goods_id = data.get("goods_id")
    quantity = _parse_positive_int(data.get("quantity"), default=1)
    check_exists = bool(data.get("check_exists", False))

    if not goods_id:
        return jsonify({"success": False, "message": "缺少商品ID"}), 400

    goods = db.session.get(Goods, goods_id)
    if not goods:
        return jsonify({"success": False, "message": "商品不存在"}), 404

    cart_item = CartItem.query.filter_by(user_id=g.user.id, goods_id=goods_id).first()
    current_quantity = cart_item.quantity if cart_item else 0
    if goods.stock < current_quantity + quantity:
        return jsonify({"success": False, "message": "库存不足"}), 400

    if cart_item:
        if check_exists:
            return jsonify({"success": False, "message": "商品已在购物车中", "code": "ALREADY_EXISTS"})
        cart_item.quantity += quantity
    else:
        db.session.add(CartItem(user_id=g.user.id, goods_id=goods_id, quantity=quantity))

    try:
        db.session.commit()
    except SQLAlchemyError:
        return _json_db_error("add_to_cart commit failed", "加入购物车失败，请稍后重试")

    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return jsonify({"success": True, "message": "已加入购物车", "quantity": current_quantity + quantity, "cart_count": cart_count}), 200


@order_bp.route("/cart/del", methods=["POST"])
def decrease_cart_item():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    data = _json_data()
    goods_id = data.get("goods_id")
    quantity = _parse_positive_int(data.get("quantity"), default=1)
    if not goods_id:
        return jsonify({"success": False, "message": "缺少商品ID"}), 400

    cart_item = CartItem.query.filter_by(user_id=g.user.id, goods_id=goods_id).first()
    if not cart_item:
        return jsonify({"success": False, "message": "购物车中不存在该商品"}), 404

    cart_item.quantity = max(cart_item.quantity - quantity, 1)
    try:
        db.session.commit()
    except SQLAlchemyError:
        return _json_db_error("decrease_cart_item commit failed", "操作失败，请稍后重试")
    return jsonify({"success": True, "message": "商品数量已减少", "quantity": cart_item.quantity})


@order_bp.route("/cart/update", methods=["POST"])
def update_cart_item():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    data = _json_data()
    item_id = data.get("item_id")
    quantity = data.get("quantity")
    if item_id is None or quantity is None:
        return jsonify({"success": False, "message": "缺少参数"}), 400

    quantity = _parse_positive_int(quantity, default=1)
    cart_item = CartItem.query.filter_by(id=item_id, user_id=g.user.id).first()
    if not cart_item:
        return jsonify({"success": False, "message": "商品不存在"}), 404
    if cart_item.goods and cart_item.goods.stock < quantity:
        return jsonify({"success": False, "message": "库存不足"}), 400

    cart_item.quantity = quantity
    try:
        db.session.commit()
    except SQLAlchemyError:
        return _json_db_error("update_cart_item commit failed", "更新失败，请稍后重试")
    subtotal = cart_item.quantity * (cart_item.goods.price if cart_item.goods else 0)
    return jsonify({"success": True, "item_subtotal": subtotal})


@order_bp.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    item_id = _json_data().get("item_id")
    if not item_id:
        return jsonify({"success": False, "message": "缺少参数"}), 400

    cart_item = CartItem.query.filter_by(id=item_id, user_id=g.user.id).first()
    if cart_item:
        try:
            db.session.delete(cart_item)
            db.session.commit()
        except SQLAlchemyError:
            return _json_db_error("remove_cart_item commit failed", "删除失败，请稍后重试")
    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return jsonify({"success": True, "cart_count": cart_count})


@order_bp.route("/cart/batch_remove", methods=["POST"])
def batch_remove_cart_items():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    item_ids = _json_data().get("item_ids", [])
    if not item_ids:
        return jsonify({"success": False, "message": "未选择商品"}), 400

    try:
        CartItem.query.filter(CartItem.id.in_(item_ids), CartItem.user_id == g.user.id).delete(synchronize_session=False)
        db.session.commit()
    except SQLAlchemyError:
        return _json_db_error("batch_remove_cart_items commit failed", "批量删除失败，请稍后重试")
    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return jsonify({"success": True, "cart_count": cart_count})


@order_bp.route("/cart/checkout", methods=["POST"])
def checkout_cart():
    auth_resp = _auth_required_json()
    if auth_resp:
        return auth_resp

    item_ids = _json_data().get("item_ids", [])
    if not item_ids:
        return jsonify({"success": False, "message": "未选择商品"}), 400

    cart_items = (
        CartItem.query.options(joinedload(CartItem.goods))
        .filter(CartItem.id.in_(item_ids), CartItem.user_id == g.user.id)
        .all()
    )
    if not cart_items:
        return jsonify({"success": False, "message": "商品无效或已失效"}), 400

    order_id = generate_orderid()
    new_order = Order(
        id=order_id,
        order_number=_generate_order_number(g.user.id),
        user_id=g.user.id,
        total_amount=0.0,
        generatetime=datetime.now(),
        payment_status="pending",
        payment_method="online",
    )
    db.session.add(new_order)
    db.session.flush()

    total_amount = 0.0
    # 从购物车快照生成订单明细，再清空已结算商品。
    for item in cart_items:
        if not item.goods:
            continue
        subtotal = item.quantity * item.goods.price
        total_amount += subtotal
        db.session.add(
            OrderItem(
                order_id=order_id,
                goods_id=item.goods_id,
                quantity=item.quantity,
                unit_price=item.goods.price,
                subtotal=subtotal,
            )
        )
        db.session.delete(item)
    new_order.total_amount = total_amount

    try:
        db.session.commit()
    except SQLAlchemyError:
        return _json_db_error("checkout_cart commit failed", "结算失败，请稍后重试")
    return jsonify({"success": True, "order_id": order_id})


@order_bp.route("/check/<order_id>", methods=["GET", "POST"])
@is_login
def checkout(order_id):
    if request.method == "POST":
        # V-CSRF-Pay vulnerability intentionally preserved for lab.
        # 保留点：POST 支付时仅按订单 ID 查询，不校验当前用户归属。
        order = Order.query.filter_by(id=order_id).first()
    else:
        order = Order.query.filter_by(id=order_id, user_id=g.user.id).first()
    if not order:
        abort(404)

    if request.method == "POST":
        if order.payment_status != "pending":
            return render_template("order/checkout.html", order=order, error="订单状态异常"), 400

        payment_method = request.form.get("payment_method", "balance")
        address_id = request.form.get("address_id")
        if address_id:
            order.address_id = address_id
        if payment_method:
            order.payment_method = payment_method
        if not g.user.balance or g.user.balance < order.total_amount:
            return render_template("order/checkout.html", order=order, error="余额不足")

        for item in order.items:
            if item.goods.stock < item.quantity:
                return render_template("order/checkout.html", order=order, error=f"商品 {item.goods.goodsname} 库存不足")
            item.goods.stock -= item.quantity

        g.user.balance -= order.total_amount
        order.payment_status = "paid"
        order.paid_at = datetime.now()
        try:
            db.session.commit()
            return render_template("order/success.html", order=order)
        except SQLAlchemyError:
            db.session.rollback()
            logger.exception("checkout payment commit failed")
            return render_template("order/checkout.html", order=order, error="支付失败，请稍后重试")

    return render_template("order/checkout.html", order=order)
