from flask import Blueprint, render_template, request, render_template_string, session, redirect, url_for, jsonify, flash
from datetime import datetime
from app.models.db import User, Order, Address, Goods, OrderItem, Voucher, db
from app.utils.tools import is_login

user_bp = Blueprint('user', __name__, url_prefix='/user')

@user_bp.route('/balance', methods=['GET'])
@is_login
def get_balance():
    user_id = session.get('user_id')
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': 'User not found'}), 404
    return jsonify({'balance': user.balance if user.balance else 0.00})

@user_bp.route('/address/list', methods=['GET'])
@is_login
def address_list():
    user_id = session.get('user_id')
    addresses = Address.query.filter_by(user_id=user_id).all()
    
    address_list = []
    for addr in addresses:
        address_list.append({
            "id": addr.id,
            "receiver": addr.receiver,
            "phone": addr.phone,
            "addressname": addr.addressname
        })
        
    return jsonify(address_list)

@user_bp.route('/voucher/redeem', methods=['POST'])
@is_login
def voucher_redeem():
    user_id = session.get('user_id')
    code = request.form.get('code') or request.args.get('code')
    if not code:
        return jsonify({'error': '缺少兑换码'}), 400
    
    voucher = Voucher.query.filter_by(code=code).first()
    if not voucher:
        return jsonify({'error': '兑换码不存在'}), 404
    if voucher.status != '0':
        return jsonify({'error': '兑换码已使用或不可用'}), 409
    if voucher.expires_at and voucher.expires_at < datetime.now():
        return jsonify({'error': '兑换码已过期'}), 400
    voucher.status = '1'
    user = User.query.get(user_id)
    if not user:
        return jsonify({'error': '用户不存在'}), 404
    
    user.balance = User.balance + voucher.amount
    
    voucher.used_by = user.id
    voucher.used_at = datetime.now()
    try:
        db.session.commit()
        refreshed = User.query.get(user_id)
        return jsonify({'message': '兑换成功', 'code': code, 'amount': voucher.amount, 'balance': refreshed.balance}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'兑换失败: {str(e)}'}), 500

@user_bp.route('/address/add', methods=['POST'])
@is_login
def add_address():
    user_id = session.get('user_id')
        
    receiver = request.form.get('receiver')
    phone = request.form.get('phone')
    addressname = request.form.get('addressname')
    
    if receiver and phone and addressname:
        new_address = Address(
            user_id=user_id,
            receiver=receiver,
            phone=phone,
            addressname=addressname
        )
        db.session.add(new_address)
        db.session.commit()
        
    return redirect(url_for('user.profile', section='address'))

@user_bp.route('/address/edit/<int:address_id>', methods=['POST'])
@is_login
def edit_address(address_id):
    user_id = session.get('user_id')
        
    address = Address.query.get(address_id)
    # IDOR Vulnerability: We are NOT checking if address.user_id == user_id
    # This allows users to edit other people's addresses if they know the ID
    
    if address:
        address.receiver = request.form.get('receiver')
        address.phone = request.form.get('phone')
        address.addressname = request.form.get('addressname')
        db.session.commit()
        
    return redirect(url_for('user.profile', section='address'))

@user_bp.route('/address/delete/<int:address_id>', methods=['POST'])
@is_login
def delete_address(address_id):
    user_id = session.get('user_id')
        
    address = Address.query.get(address_id)
    # IDOR Vulnerability: No ownership check
    
    if address:
        db.session.delete(address)
        db.session.commit()
        
    return redirect(url_for('user.profile', section='address'))




@user_bp.route('/profile', methods=['GET', 'POST'])
@is_login
def profile():
    user_id = session.get('user_id')
        
    user = User.query.get(user_id)
    if not user:
        return redirect(url_for('auth.login'))

    section = request.args.get('section', 'orders')
    if request.method == 'POST' and section == 'info':
        new_username = request.form.get('username', '').strip()
        new_password = request.form.get('password', '').strip()
        updated = False
        if new_username:
            user.username = new_username
            updated = True
        if new_password:
            user.password = new_password
            updated = True
        if updated:
            try:
                db.session.commit()
                flash('个人信息已更新', 'success')
            except Exception as e:
                db.session.rollback()
                flash('更新失败: ' + str(e), 'danger')
        return redirect(url_for('user.profile', section='info'))

    data = {"page": "profile", "section": section}
    
    if section == 'orders':
        orders = Order.query.filter_by(user_id=user_id).order_by(Order.generatetime.desc()).all()
        data['orders'] = []
        status_map = {
            'pending': ('待付款', 'pending'),
            'paid': ('已支付', 'active'),
            'shipped': ('已发货', 'pending'),
            'completed': ('已完成', 'active'),
            'cancelled': ('已取消', 'inactive'),
        }
        for order in orders:
            label, cls = status_map.get(order.payment_status or 'pending', ('待付款', 'pending'))
            data['orders'].append({
                "id": order.id, # Using ID for link
                "display_id": order.order_number, # Display friendly ID
                "date": order.generatetime.strftime('%Y-%m-%d') if order.generatetime else '',
                "total": order.total_amount,
                "status_label": label,
                "status_class": cls
            })
    elif section == 'address':
        addresses = Address.query.filter_by(user_id=user_id).all()
        data['addresses'] = []
        for addr in addresses:
            data['addresses'].append({
                "id": addr.id,
                "receiver": addr.receiver,
                "phone": addr.phone,
                "addressname": addr.addressname
            })
    elif section == 'assets':
        data['assets'] = {
            "balance": user.balance if user.balance else 0.00,
            "points": 0 # Not in DB
        }
    elif section == 'info':
        data['info'] = {
            "username": user.username,
            "email": user.email
        }
    
    return render_template('user/profile.html', data=data)

@user_bp.route('/order/<order_id>', methods=['GET'])
@is_login
def order_detail(order_id):
    from app.utils.tools import query_order_detail_raw
    raw = query_order_detail_raw(order_id)
    if not raw:
        return "Order not found", 404
    shipping_info = ""
    if raw.get('address'):
        a = raw['address']
        shipping_info = f"{a.get('receiver','')}, {a.get('phone','')}, {a.get('addressname','')}"
    products = []
    for it in raw.get('items', []):
        products.append({
            "name": it.get('goodsname') or "Unknown",
            "price": it.get('unit_price'),
            "quantity": it.get('quantity')
        })
    o = raw['order']
    date_val = o.get('generatetime')
    try:
        date_str = date_val.strftime('%Y-%m-%d') if isinstance(date_val, datetime) else (str(date_val) if date_val is not None else '')
    except Exception:
        date_str = str(date_val) if date_val is not None else ''
    order_data = {
        "id": o.get('order_number'),
        "products": products,
        "total": o.get('total_amount'),
        "date": date_str,
        "shipping_info": shipping_info
    }
    
    # V-SSTI: Server-Side Template Injection  # The vulnerability exists because we format the string with user input BEFORE rendering the template
    # Simulating a user-controlled value (e.g., username from session or profile)
    username = request.args.get('username')
    if not username:
        # Try to get from session
        user_id = session.get('user_id')
        if user_id:
            user = User.query.get(user_id)
            if user:
                username = user.username
    if not username:
        username = 'HackShop User'
    
    # VULNERABLE CODE: Direct concatenation of user input into template string
    template_str = f"""
    <div class="modal-header">
        <h5 class="modal-title">订单详情 - {username}</h5>
        <button type="button" class="btn-close" data-bs-dismiss="modal" aria-label="Close"></button>
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
