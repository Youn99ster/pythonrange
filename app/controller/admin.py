from flask import Blueprint, render_template, request, flash, redirect, url_for, session, Response, jsonify
import os
import io
import urllib.request
from datetime import datetime, timedelta
from app.models.db import db, Admin, Voucher, Goods, User, Order
from sqlalchemy import func
from sqlalchemy.orm import joinedload, selectinload
from app.utils.tools import admin_auth, generate_voucher_code, is_admin_login, unique_filename
try:
    from openpyxl import Workbook, load_workbook
except Exception:
    Workbook = None
    load_workbook = None

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    """
    Admin Login Page (F-402)
    Vulnerability: V-Admin-AES
    The password sent from frontend is AES encrypted with a hardcoded key.
    """
    if request.method == 'POST':
        username = request.form.get('username')
        encrypted_password = request.form.get('password') # Encrypted string from frontend
        
        if not username or not encrypted_password:
             flash('请输入用户名和密码', 'danger')
             return render_template('admin/login.html')
        if admin_auth(username, encrypted_password):
            session['admin_logged_in'] = True
            session['admin_user'] = username
            flash('登录成功！欢迎回来，管理员。', 'success')
            return redirect(url_for('admin.dashboard'))
        else:
             flash('用户名或密码错误', 'danger')
            
    # Check if hint should be shown (Only if admin has never logged in)
    admin_user = Admin.query.filter_by(username='admin').first()
    if admin_user and admin_user.last_login is None:
            flash(f'管理员初始账号：{admin_user.username} 密码：{admin_user.password}', 'info')

    return render_template('admin/login.html')

@admin_bp.route('/dashboard')
@is_admin_login
def dashboard():
    total_sales = db.session.query(func.coalesce(func.sum(Order.total_amount), 0.0)).scalar()
    orders_count = Order.query.count()
    users_count = User.query.count()
    goods_count = Goods.query.count()
    page = request.args.get('page', 1, type=int)
    since = datetime.now() - timedelta(days=30)
    recent_q = (
        Order.query.options(joinedload(Order.user), selectinload(Order.items))
        .filter(Order.generatetime != None, Order.generatetime >= since)
        .order_by(Order.generatetime.desc())
    )
    pagination = recent_q.paginate(page=page, per_page=10, error_out=False)
    recent = pagination.items
    recent_orders = []
    status_map = {
        'pending': ('待付款', 'pending'),
        'paid': ('已支付', 'active'),
        'shipped': ('已发货', 'pending'),
        'completed': ('已完成', 'active'),
        'cancelled': ('已取消', 'inactive'),
    }
    for o in recent:
        label, cls = status_map.get(o.payment_status or 'pending', ('待付款', 'pending'))
        product_name = ''
        product_quantity = 0
        try:
            if o.items:
                first_item = o.items[0]
                product_name = first_item.goods.goodsname if first_item.goods else ''
                product_quantity = sum([it.quantity or 0 for it in o.items])
        except Exception:
            product_name = ''
            product_quantity = 0
        recent_orders.append({
            'order_number': o.order_number,
            'username': o.user.username if o.user else '',
            'amount': o.total_amount or 0.0,
            'status_label': label,
            'status_class': cls,
            'product_name': product_name,
            'product_quantity': product_quantity,
            'date': o.generatetime.strftime('%Y-%m-%d %H:%M') if o.generatetime else ''
        })
    stats = {
        'total_sales': float(total_sales or 0.0),
        'orders_count': orders_count,
        'users_count': users_count,
        'goods_count': goods_count
    }
    return render_template('admin/dashboard.html', stats=stats, recent_orders=recent_orders, pagination=pagination)

@admin_bp.route('/products')
@is_admin_login
def products():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    keyword = (request.args.get('keyword') or '').strip()
    status = (request.args.get('status') or '').strip()
    q = Goods.query
    if keyword:
        like_kw = f"%{keyword}%"
        q = q.filter((Goods.goodsname.ilike(like_kw)) | (Goods.category.ilike(like_kw)))
    if status in ('0', '1'):
        q = q.filter(Goods.status == status)
    pagination = q.order_by(Goods.id.desc()).paginate(page=page, per_page=per_page, error_out=False)
    batch_url = request.args.get('batch_url', '')
    return render_template(
        'admin/products.html',
        goods=pagination.items,
        pagination=pagination,
        batch_url=batch_url,
        keyword=keyword,
        status=status
    )

@admin_bp.route('/orders')
@is_admin_login
def orders():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    keyword = (request.args.get('keyword') or '').strip()
    status_filter = (request.args.get('status') or '').strip()
    q = Order.query.options(joinedload(Order.user), selectinload(Order.items))
    if keyword:
        like_kw = f"%{keyword}%"
        q = q.join(Order.user).filter((Order.order_number.ilike(like_kw)) | (User.username.ilike(like_kw)))
    if status_filter in ('pending', 'paid', 'shipped', 'completed', 'cancelled'):
        q = q.filter(Order.payment_status == status_filter)
    pagination = q.order_by(Order.generatetime.desc()).paginate(page=page, per_page=per_page, error_out=False)
    status_map = {
        'pending': ('待付款', 'pending'),
        'paid': ('已支付', 'active'),
        'shipped': ('已发货', 'pending'),
        'completed': ('已完成', 'active'),
        'cancelled': ('已取消', 'inactive'),
    }
    orders = []
    for o in pagination.items:
        product = ''
        try:
            if o.items:
                first_item = o.items[0]
                name = first_item.goods.goodsname if first_item.goods else ''
                qty = first_item.quantity or 0
                product = f"{name} x{qty}"
        except Exception:
            product = ''
        label, cls = status_map.get(o.payment_status or 'pending', ('待付款', 'pending'))
        orders.append({
            'order_number': o.order_number,
            'username': o.user.username if o.user else '',
            'product': product,
            'amount': o.total_amount or 0.0,
            'payment_status': o.payment_status or 'pending',
            'status_label': label,
            'status_class': cls,
            'date': o.generatetime.strftime('%Y-%m-%d %H:%M') if o.generatetime else ''
        })
    return render_template(
        'admin/orders.html',
        orders=orders,
        pagination=pagination,
        keyword=keyword,
        status_filter=status_filter
    )

@admin_bp.route('/users')
@is_admin_login
def users():
    admins = Admin.query.order_by(Admin.id.asc()).all()
    return render_template('admin/users.html', admins=admins)

@admin_bp.route('/settings')
@is_admin_login
def settings():
    return render_template('admin/settings.html')

@admin_bp.route('/vouchers')
@is_admin_login
def vouchers():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    pagination = Voucher.query.order_by(Voucher.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False)
    
    return render_template('admin/vouchers.html', vouchers=pagination.items, pagination=pagination)

@admin_bp.route('/vouchers/generate', methods=['POST'])
@is_admin_login
def generate_vouchers():

        
    amount = request.form.get('amount', type=float)
    count = request.form.get('count', type=int, default=1)
    
    if not amount:
        flash('请输入金额', 'danger')
        return redirect(url_for('admin.vouchers'))
        
    generated_count = 0
    for _ in range(count):
        # Generate random code: HACK-XXXX-XXXX
        code = generate_voucher_code()
        
        # Check if exists (though highly unlikely)
        if Voucher.query.filter_by(code=code).first():
            continue
            
        voucher = Voucher(
            code=code,
            amount=amount,
            status='0',
            expires_at=datetime.now() + timedelta(days=365) # 1 year validity
        )
        db.session.add(voucher)
        generated_count += 1
        
    try:
        db.session.commit()
        flash(f'成功生成 {generated_count} 张面值 ¥{amount} 的储值券', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'生成失败: {str(e)}', 'danger')
        
    return redirect(url_for('admin.vouchers'))

@admin_bp.route('/product/add', methods=['POST'])
@is_admin_login
def product_add():
    goodsname = request.form.get('goodsname', '').strip()
    category = request.form.get('category', '').strip()
    price = request.form.get('price', type=float, default=0.0)
    stock = request.form.get('stock', type=int, default=0)
    mainimg = ''
    content = request.form.get('content', '').strip()
    status = request.form.get('status', '').strip() or '0'
    image = request.files.get('image')
    if not goodsname or not category:
        flash('请填写商品名称与分类', 'danger')
        return redirect(url_for('admin.products'))
    if image and image.filename:
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = unique_filename(image.filename)
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        mainimg = '/uploads/' + filename
    goods = Goods(
        goodsname=goodsname,
        category=category,
        mainimg=mainimg or 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800',
        content=content,
        stock=stock,
        price=price,
        status=status
    )
    try:
        db.session.add(goods)
        db.session.commit()
        flash('商品添加成功', 'success')
    except Exception as e:
        db.session.rollback()
        flash('商品添加失败: ' + str(e), 'danger')
    return redirect(url_for('admin.products'))

@admin_bp.route('/product/<int:goods_id>/edit', methods=['POST'])
@is_admin_login
def product_edit(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    goodsname = request.form.get('goodsname', '').strip()
    category = request.form.get('category', '').strip()
    price = request.form.get('price', type=float, default=0.0)
    stock = request.form.get('stock', type=int, default=0)
    content = request.form.get('content', '').strip()
    status = request.form.get('status', '').strip() or goods.status or '0'
    if not goodsname or not category:
        flash('璇峰～鍐欏晢鍝佸悕绉颁笌鍒嗙被', 'danger')
        return redirect(url_for('admin.products'))
    goods.goodsname = goodsname
    goods.category = category
    goods.price = price
    goods.stock = stock
    goods.content = content
    goods.status = status
    image = request.files.get('image')
    if image and image.filename:
        upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
        os.makedirs(upload_dir, exist_ok=True)
        filename = unique_filename(image.filename)
        filepath = os.path.join(upload_dir, filename)
        image.save(filepath)
        goods.mainimg = '/uploads/' + filename
    try:
        db.session.commit()
        flash('鍟嗗搧淇敼鎴愬姛', 'success')
    except Exception as e:
        db.session.rollback()
        flash('鍟嗗搧淇敼澶辫触: ' + str(e), 'danger')
    return redirect(url_for('admin.products'))

@admin_bp.route('/product/<int:goods_id>/toggle', methods=['POST'])
@is_admin_login
def product_toggle(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    goods.status = '1' if (goods.status or '0') == '0' else '0'
    try:
        db.session.commit()
        flash('鍟嗗搧鐘舵€佸凡鏇存柊', 'success')
    except Exception as e:
        db.session.rollback()
        flash('鏇存柊澶辫触: ' + str(e), 'danger')
    return redirect(url_for('admin.products'))

@admin_bp.route('/product/<int:goods_id>/delete', methods=['POST'])
@is_admin_login
def product_delete(goods_id):
    goods = Goods.query.get_or_404(goods_id)
    try:
        # Use soft delete to avoid FK conflicts with existing order_items.
        goods.status = '1'
        db.session.commit()
        flash('鍟嗗搧宸蹭笅鏋?', 'success')
    except Exception as e:
        db.session.rollback()
        flash('鍒犻櫎澶辫触: ' + str(e), 'danger')
    return redirect(url_for('admin.products'))

@admin_bp.route('/order/<order_number>/status', methods=['POST'])
@is_admin_login
def order_update_status(order_number):
    next_status = (request.form.get('status') or '').strip()
    allowed = {'pending', 'paid', 'shipped', 'completed', 'cancelled'}
    if next_status not in allowed:
        flash('闈炴硶鐘舵€?', 'danger')
        return redirect(url_for('admin.orders'))
    order = Order.query.filter_by(order_number=order_number).first_or_404()
    order.payment_status = next_status
    if next_status == 'paid' and not order.paid_at:
        order.paid_at = datetime.now()
    try:
        db.session.commit()
        flash('璁㈠崟鐘舵€佹洿鏂版垚鍔?', 'success')
    except Exception as e:
        db.session.rollback()
        flash('鏇存柊澶辫触: ' + str(e), 'danger')
    return redirect(url_for('admin.orders'))

@admin_bp.route('/logout')
@is_admin_login
def logout():
    session.clear()
    flash('您已退出登录', 'info')
    return redirect(url_for('admin.login'))

# Batch import template (XLSX) download
@admin_bp.route('/products/batch/template', methods=['GET'])
@is_admin_login
def products_batch_template():
    if Workbook is None:
        return Response("openpyxl 未安装，无法生成xlsx模板", status=500)
    wb = Workbook()
    ws = wb.active
    ws.title = "products"
    headers = ["goodsname", "category", "price", "stock", "status", "mainimg", "content"]
    ws.append(headers)
    ws.append(["示例商品A", "手机数码", 1999.99, 100, "0", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800", "这是一个示例商品"])
    ws.append(["示例商品B", "电脑办公", 2999.00, 50, "0", "https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800", "这是第二个示例商品"])
    buf = io.BytesIO()
    wb.save(buf)
    buf.seek(0)
    return Response(
        buf.getvalue(),
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={'Content-Disposition': 'attachment; filename=products_template.xlsx'}
    )

# Step 1: Upload XLSX file to /uploads and return URL
@admin_bp.route('/products/batch/upload', methods=['POST'])
@is_admin_login
def products_batch_upload():
    file = request.files.get('file')
    if not file or not file.filename:
        return jsonify({'error': '请上传文件'}), 400
    if not file.filename.lower().endswith('.xlsx'):
        return jsonify({'error': '仅支持上传 .xlsx 文件'}), 400
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
    os.makedirs(upload_dir, exist_ok=True)
    filename = unique_filename(file.filename)
    filepath = os.path.join(upload_dir, filename)
    file.save(filepath)
    url =  'http://'+request.host+'/uploads/' + filename
    return jsonify({'url': url})

# Step 2: Import by fetching the provided URL (SSRF vulnerability)
@admin_bp.route('/products/batch/import', methods=['POST'])
@is_admin_login
def products_batch_import():
    url = request.form.get('url', '').strip()
    if not url:
        return jsonify({'success': False, 'error': '缺少文件URL'}), 400
    try:
        # SSRF: directly request the URL provided by admin without validation
        with urllib.request.urlopen(url) as resp:
            data_bytes = resp.read()
    except Exception as e:
        return jsonify({'success': False, 'error': f'获取文件失败: {str(e)}'}), 400

    try:
        if load_workbook is None:
            raise RuntimeError("openpyxl 未安装，无法解析xlsx")
        wb = load_workbook(filename=io.BytesIO(data_bytes), data_only=True)
        ws = wb.active
        rows = list(ws.iter_rows(values_only=True))
        if not rows:
            raise ValueError("文件为空")
        headers = [str(h).strip() if h is not None else '' for h in rows[0]]
        imported = 0
        for r in rows[1:]:
            row = dict(zip(headers, r))
            goodsname = (str(row.get('goodsname') or '')).strip()
            category = (str(row.get('category') or '')).strip()
            price_val = row.get('price')
            stock_val = row.get('stock')
            status = (str(row.get('status') or '0')).strip()
            mainimg = (str(row.get('mainimg') or '')).strip() or 'https://images.unsplash.com/photo-1523275335684-37898b6baf30?w=800'
            content = (str(row.get('content') or '')).strip()
            try:
                price = float(price_val or 0.0)
            except Exception:
                price = 0.0
            try:
                stock = int(float(stock_val or 0))
            except Exception:
                stock = 0
            if not goodsname or not category:
                continue
            goods = Goods(
                goodsname=goodsname,
                category=category,
                mainimg=mainimg,
                content=content,
                stock=stock,
                price=price,
                status=status
            )
            db.session.add(goods)
            imported += 1
        db.session.commit()
        return jsonify({'success': True, 'imported': imported})
    except Exception as e:
        db.session.rollback()
        preview = None
        try:
            preview = data_bytes.decode('utf-8', errors='ignore')
        except Exception:
            preview = None
        if preview:
            # Limit preview size
            preview = preview[:5000]
        return jsonify({'success': False, 'error': f'导入失败: {str(e)}', 'preview': preview, 'url': url}), 400
