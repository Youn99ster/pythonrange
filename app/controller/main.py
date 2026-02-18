from flask import Blueprint, render_template, request, jsonify, abort, g, send_from_directory, flash, redirect, url_for
import os
import json
from app.models.db import MailLog, db, Goods, CartItem, Admin, GoodsImage, GoodsSpec
from app.utils.tools import generate_mailcode
from app.utils.db import redis_client

main_bp = Blueprint('main',__name__)

@main_bp.route('/',methods=['GET'])
def index():
    goods = Goods.query.filter_by(status='0').all() # Only show active products (status='0' based on init script)

    return render_template('main/index.html', goods=goods)

@main_bp.route('/product-detail/<int:id>',methods=['GET'])
def product_detail(id):
    product = Goods.query.get(id)
    if not product:
        abort(404)
    return render_template('main/product-detail.html', product=product)


@main_bp.route('/search/<query>',methods=['GET'])
def search(query):
    data = {"page":"search page","query":query}
    return render_template('main/search.html',data=data)

@main_bp.route('/inbox',methods=['GET','POST'])
def inbox():
    mails = MailLog.query.order_by(MailLog.created_at.desc()).all()
    return render_template('main/inbox.html', mail_list=mails)

@main_bp.route('/send_mail', methods=['POST'])
def send_mail():
    payload = request.get_json(silent=True) if request.is_json else request.form
    email = payload.get('email')
    if not email or not isinstance(email, str):
        return jsonify({"status": "error", "message": "缺少或非法的邮箱参数"}), 400
    code = generate_mailcode()
    try:
        redis_client.setex(f"mailcode:{email}", 600, code)
        mail_log = MailLog(subject='验证码', sender='system@hackshop.local', receiver=email, content=f'{email},您的验证码是 {code}。')
        db.session.add(mail_log)
        db.session.commit()
    except Exception as e:
        return jsonify({"status": "error", "message": "Redis写入失败"}), 500
    return jsonify({"status": "ok", "message": "验证码已发送", "email": email}), 200

@main_bp.route('/api/mails', methods=['GET'])
def api_mails():
    since_id = request.args.get('since_id', type=int)
    query = MailLog.query
    if since_id:
        query = query.filter(MailLog.id > since_id)
    mails = query.order_by(MailLog.created_at.desc()).all()
    data = []
    for m in mails:
        data.append({
            "id": m.id,
            "subject": m.subject,
            "sender": m.sender,
            "receiver": m.receiver,
            "content": m.content,
            "created_at": m.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            "is_read": m.is_read,
        })
    return jsonify(data)

@main_bp.route('/api/mail/<int:mail_id>/read', methods=['POST'])
def api_mail_read(mail_id: int):
    is_read = True
    payload = request.get_json(silent=True) if request.is_json else {}
    if 'is_read' in payload:
        is_read = bool(payload.get('is_read'))
    mail = db.session.get(MailLog, mail_id)
    if not mail:
        return jsonify({"status": "error", "message": "邮件不存在"}), 404
    mail.is_read = is_read
    db.session.commit()
    return jsonify({"status": "ok", "id": mail.id, "is_read": mail.is_read})

@main_bp.route('/uploads/<path:filename>')
def uploads(filename):
    upload_dir = os.path.join(os.path.dirname(__file__), '..', 'uploads')
    return send_from_directory(upload_dir, filename)

@main_bp.route('/setup', methods=['GET', 'POST'])
def setup():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
    json_path = os.path.join(project_root, 'product.json')
    lock_path = os.path.join(project_root, 'product.json.lock')
    has_product_json = os.path.exists(json_path)
    is_locked = os.path.exists(lock_path) or (not has_product_json)
    can_init = has_product_json and (not os.path.exists(lock_path))

    if request.method == 'POST' and (not can_init):
        flash('系统已初始化，请勿重复提交', 'warning')
        return redirect(url_for('main.setup'))

    if request.method == 'GET' and is_locked:
        flash('系统已初始化，请勿重复提交', 'warning')

    # Summary info
    goods_count = Goods.query.count()
    admin = Admin.query.filter_by(username='admin').first()
    status = {
        "goods_count": goods_count,
        "has_admin": bool(admin),
        "has_product_json": has_product_json,
        "is_locked": is_locked,
        "can_init": can_init,
    }
    if request.method == 'POST':
        # Admin init
        admin_username = request.form.get('admin_username', 'admin').strip()
        admin_password = request.form.get('admin_password', 'admin123').strip()
        if not admin_username:
            admin_username = 'admin'
        if not admin_password:
            admin_password = 'admin123'
        existing_admin = Admin.query.filter_by(username=admin_username).first()
        if existing_admin:
            existing_admin.password = admin_password
        else:
            new_admin = Admin(username=admin_username, password=admin_password)
            db.session.add(new_admin)
        # Products init
        init_products = request.form.get('init_products', 'on')
        imported = 0
        skipped = 0
        if str(init_products).lower() in ('on', 'true', '1', 'yes'):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    products = json.load(f)
                for p in products:
                    slug = (p.get('slug') or '').strip()
                    if slug and Goods.query.filter_by(slug=slug).first():
                        skipped += 1
                        continue
                    goods = Goods(
                        goodsname=p.get('goodsname') or '',
                        category=p.get('category') or '',
                        mainimg=p.get('mainimg') or '',
                        content=p.get('content') or '',
                        stock=int(p.get('stock') or 0),
                        price=float(p.get('price') or 0.0),
                        status=str(p.get('status') or '0'),
                        brand=p.get('brand'),
                        model=p.get('model'),
                        original_price=float(p.get('original_price') or 0.0) if p.get('original_price') is not None else None,
                        rating_avg=float(p.get('rating_avg') or 0.0),
                        rating_count=int(p.get('rating_count') or 0),
                        sales_count=int(p.get('sales_count') or 0),
                        slug=slug or None
                    )
                    db.session.add(goods)
                    db.session.flush()
                    images = p.get('images') or []
                    for img in images:
                        gi = GoodsImage(
                            goods_id=goods.id,
                            url=img.get('url') or '',
                            is_main=bool(img.get('is_main')),
                            sort_order=int(img.get('sort_order') or 0)
                        )
                        db.session.add(gi)
                    specs = p.get('specs') or []
                    for sp in specs:
                        gs = GoodsSpec(
                            goods_id=goods.id,
                            name=sp.get('name') or '',
                            value=sp.get('value') or '',
                            sort_order=int(sp.get('sort_order') or 0)
                        )
                        db.session.add(gs)
                    imported += 1
            except Exception as e:
                db.session.rollback()
                flash('初始化失败: ' + str(e), 'danger')
                return redirect(url_for('main.setup'))
        try:
            db.session.commit()
            if can_init and os.path.exists(json_path):
                try:
                    os.replace(json_path, lock_path)
                except Exception:
                    pass
            flash(
                f'初始化成功：管理员{"已更新" if existing_admin else "已创建"}；商品导入 {imported} 条，跳过 {skipped} 条',
                'success'
            )
            base_url = request.host_url.rstrip('/')
            flash(
                f'管理后台地址: {base_url}/admin/login ，账号: {admin_username} ，密码: {admin_password} 。'
                f'请使用该账号登录后台，按 PRD 文档测试 10 个漏洞场景。',
                'info'
            )
        except Exception as e:
            db.session.rollback()
            flash('提交失败: ' + str(e), 'danger')
        return redirect(url_for('main.setup'))
    return render_template('setup.html', status=status)
