from datetime import datetime

from flask import Blueprint, abort, g, jsonify, redirect, render_template, request, url_for
from sqlalchemy.orm import joinedload

from app.models.db import CartItem, Goods, Order, OrderItem, db
from app.utils.tools import generate_orderid, is_login

order_bp = Blueprint("order", __name__, url_prefix="/order")


def _json_data():
    return request.get_json(silent=True) or {}


def _parse_positive_int(raw, default=1):
    try:
        value = int(raw)
        return value if value > 0 else default
    except (TypeError, ValueError):
        return default


@order_bp.app_context_processor
def inject_cart_count():
    if hasattr(g, "user") and g.user:
        try:
            count = CartItem.query.filter_by(user_id=g.user.id).count()
            return dict(cart_count=count)
        except Exception:
            pass
    return dict(cart_count=0)


@order_bp.route("/cart")
def cart():
    if not g.user:
        return redirect(url_for("auth.login"))

    cart_items = (
        CartItem.query.options(joinedload(CartItem.goods))
        .filter_by(user_id=g.user.id)
        .all()
    )

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
    if not g.user:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "请先登录",
                    "redirect": url_for("auth.login"),
                }
            ),
            401,
        )

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
    new_quantity = current_quantity + quantity
    if goods.stock < new_quantity:
        return jsonify({"success": False, "message": "库存不足"}), 400

    if cart_item:
        if check_exists:
            return jsonify(
                {
                    "success": False,
                    "message": "该商品已经加入购物车",
                    "code": "ALREADY_EXISTS",
                }
            )
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=g.user.id, goods_id=goods_id, quantity=quantity)
        db.session.add(cart_item)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "添加失败", "error": str(e)}), 500

    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return (
        jsonify(
            {
                "success": True,
                "message": "已添加到购物车",
                "quantity": cart_item.quantity,
                "cart_count": cart_count,
            }
        ),
        200,
    )


@order_bp.route("/cart/del", methods=["POST"])
def decrease_cart_item():
    if not g.user:
        return (
            jsonify(
                {
                    "success": False,
                    "message": "请先登录",
                    "redirect": url_for("auth.login"),
                }
            ),
            401,
        )

    data = _json_data()
    goods_id = data.get("goods_id")
    quantity = _parse_positive_int(data.get("quantity"), default=1)
    if not goods_id:
        return jsonify({"success": False, "message": "缺少商品ID"}), 400

    cart_item = CartItem.query.filter_by(user_id=g.user.id, goods_id=goods_id).first()
    if not cart_item:
        return jsonify({"success": False, "message": "商品不在购物车中"}), 404

    new_quantity = cart_item.quantity - quantity
    cart_item.quantity = max(new_quantity, 1)

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "操作失败", "error": str(e)}), 500
    return jsonify({"success": True, "message": "已减少商品数量", "quantity": cart_item.quantity})


@order_bp.route("/cart/update", methods=["POST"])
def update_cart_item():
    if not g.user:
        return jsonify({"success": False, "message": "请先登录"}), 401

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
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "更新失败", "error": str(e)}), 500

    item_subtotal = cart_item.quantity * (cart_item.goods.price if cart_item.goods else 0)
    return jsonify({"success": True, "item_subtotal": item_subtotal})


@order_bp.route("/cart/remove", methods=["POST"])
def remove_cart_item():
    if not g.user:
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = _json_data()
    item_id = data.get("item_id")
    if not item_id:
        return jsonify({"success": False, "message": "缺少参数"}), 400

    cart_item = CartItem.query.filter_by(id=item_id, user_id=g.user.id).first()
    if cart_item:
        try:
            db.session.delete(cart_item)
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            return jsonify({"success": False, "message": "删除失败", "error": str(e)}), 500

    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return jsonify({"success": True, "cart_count": cart_count})


@order_bp.route("/cart/batch_remove", methods=["POST"])
def batch_remove_cart_items():
    if not g.user:
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = _json_data()
    item_ids = data.get("item_ids", [])
    if not item_ids:
        return jsonify({"success": False, "message": "未选择商品"}), 400

    try:
        CartItem.query.filter(
            CartItem.id.in_(item_ids), CartItem.user_id == g.user.id
        ).delete(synchronize_session=False)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "批量删除失败", "error": str(e)}), 500

    cart_count = CartItem.query.filter_by(user_id=g.user.id).count()
    return jsonify({"success": True, "cart_count": cart_count})


@order_bp.route("/cart/checkout", methods=["POST"])
def checkout_cart():
    if not g.user:
        return jsonify({"success": False, "message": "请先登录"}), 401

    data = _json_data()
    item_ids = data.get("item_ids", [])
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
    order_number = datetime.now().strftime("%Y%m%d%H%M%S") + str(g.user.id).zfill(4)
    total_amount = 0.0

    new_order = Order(
        id=order_id,
        order_number=order_number,
        user_id=g.user.id,
        total_amount=0.0,
        generatetime=datetime.now(),
        payment_status="pending",
        payment_method="online",
    )
    db.session.add(new_order)
    db.session.flush()

    for item in cart_items:
        if not item.goods:
            continue
        item_subtotal = item.quantity * item.goods.price
        total_amount += item_subtotal
        db.session.add(
            OrderItem(
                order_id=order_id,
                goods_id=item.goods_id,
                quantity=item.quantity,
                unit_price=item.goods.price,
                subtotal=item_subtotal,
            )
        )
        db.session.delete(item)

    new_order.total_amount = total_amount
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": "结算失败", "error": str(e)}), 500

    return jsonify({"success": True, "order_id": order_id})


@order_bp.route("/check/<order_id>", methods=["GET", "POST"])
@is_login
def checkout(order_id):
    if request.method == "POST":
        # V-CSRF-Pay vulnerability intentionally preserved for lab.
        order = Order.query.filter_by(id=order_id).first()
    else:
        order = Order.query.filter_by(id=order_id, user_id=g.user.id).first()

    if not order:
        abort(404)

    if request.method == "POST":
        if order.payment_status != "pending":
            return render_template("error.html", message="订单状态异常"), 400

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
                return render_template(
                    "order/checkout.html",
                    order=order,
                    error=f"商品 {item.goods.goodsname} 库存不足",
                )
            item.goods.stock -= item.quantity

        g.user.balance -= order.total_amount
        order.payment_status = "paid"
        order.paid_at = datetime.now()

        try:
            db.session.commit()
            return render_template("order/success.html", order=order)
        except Exception as e:
            db.session.rollback()
            return render_template(
                "order/checkout.html", order=order, error=f"支付处理失败: {e}"
            )

    return render_template("order/checkout.html", order=order)
