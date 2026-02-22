"""
HackShop 数据模型定义模块。

包含以下核心模型：
- Admin       : 管理员账号
- MailLog     : 站内信 / 邮件日志（验证码、密码重置等）
- User        : 前台用户
- Address     : 用户收货地址
- Goods       : 商品（含图片、规格子表）
- GoodsImage  : 商品轮播图
- GoodsSpec   : 商品规格参数
- CartItem    : 购物车条目
- Voucher     : 储值券 / 代金券
- Order       : 订单主表
- OrderItem   : 订单明细行

关系概览：
  User  1──N  Order  1──N  OrderItem  N──1  Goods
  User  1──N  Address
  User  M──N  Goods（收藏，通过 user_goods 中间表）
  Goods 1──N  GoodsImage / GoodsSpec
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum, Numeric


db = SQLAlchemy()

# ---- 业务状态常量 ----
GOODS_ON_SALE = "0"      # 商品上架
GOODS_OFF_SALE = "1"     # 商品下架
VOUCHER_UNUSED = "0"     # 储值券未使用
VOUCHER_USED = "1"       # 储值券已使用

# ---- 多对多中间表：用户收藏商品 ----
user_goods = db.Table(
    'user_goods',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id')),
    db.Column('goods_id', db.Integer, db.ForeignKey('goods.id'))
)


# ===================== 管理员 =====================
class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Admin {self.username}>"


# ===================== 站内信日志 =====================
class MailLog(db.Model):
    """站内邮件记录，用于模拟验证码发送和密码重置邮件。"""
    __tablename__ = 'mail_logs'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)


# ===================== 前台用户 =====================
class User(db.Model):
    """前台注册用户，靶场保留明文密码以演示认证风险。"""
    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    email = db.Column(db.String(100), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    balance = db.Column(Numeric(10, 2))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    goods = db.relationship('Goods', secondary=user_goods, back_populates='users')
    orders = db.relationship('Order', backref='user')
    addresses = db.relationship('Address', backref='user')
    vouchers = db.relationship('Voucher', backref='user')


# ===================== 收货地址 =====================
class Address(db.Model):
    """用户收货地址。V-IDOR-Modify 漏洞：编辑/删除接口未校验归属。"""
    __tablename__ = "address"
    id = db.Column(db.Integer, primary_key=True)
    receiver = db.Column(db.String(16), nullable=False)
    phone = db.Column(db.String(256), nullable=False)
    addressname = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    orders = db.relationship('Order', backref='address')

    def __repr__(self):
        return f"<Address {self.receiver} {self.addressname}>"


# ===================== 商品 =====================
class Goods(db.Model):
    """商品主表，status='0' 上架 / '1' 下架。"""
    __tablename__ = "goods"
    id = db.Column(db.Integer, primary_key=True)
    goodsname = db.Column(db.String(256), nullable=False)
    category = db.Column(db.String(256), nullable=False)
    mainimg = db.Column(db.String(1024), nullable=False)
    content = db.Column(db.Text, nullable=False)
    stock = db.Column(db.Integer, nullable=False)
    price = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(db.String(1), default=GOODS_ON_SALE)
    brand = db.Column(db.String(128))
    model = db.Column(db.String(256))
    original_price = db.Column(Numeric(10, 2))
    rating_avg = db.Column(db.Float, default=0.0, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    sales_count = db.Column(db.Integer, default=0, nullable=False)
    slug = db.Column(db.String(256), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    users = db.relationship('User', secondary=user_goods, back_populates='goods')   # 收藏该商品的用户
    order_items = db.relationship('OrderItem', back_populates='goods')              # 关联的订单明细
    images = db.relationship('GoodsImage', back_populates='goods', cascade='all, delete-orphan')  # 轮播图
    specs = db.relationship('GoodsSpec', back_populates='goods', cascade='all, delete-orphan')    # 规格参数

    def __repr__(self):
        return f"<Goods {self.goodsname}>"


# ===================== 商品轮播图 =====================
class GoodsImage(db.Model):
    """商品图片，is_main 标记主图，sort_order 控制展示顺序。"""
    __tablename__ = "goods_images"
    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    is_main = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    goods = db.relationship('Goods', back_populates='images')

    def __repr__(self):
        return f"<GoodsImage goods={self.goods_id} url={self.url}>"


# ===================== 商品规格参数 =====================
class GoodsSpec(db.Model):
    """商品规格键值对，如 "颜色: 黑色"、"内存: 8GB"。"""
    __tablename__ = "goods_specs"
    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(512), nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    goods = db.relationship('Goods', back_populates='specs')

    def __repr__(self):
        return f"<GoodsSpec {self.name}={self.value}>"


# ===================== 购物车 =====================
class CartItem(db.Model):
    """购物车条目，每个用户对同一商品只保留一条记录，通过 quantity 累加。"""
    __tablename__ = "cart_items"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    
    user = db.relationship('User', backref=db.backref('cart_items', lazy=True))
    goods = db.relationship('Goods', backref=db.backref('cart_items', lazy=True))

    def __repr__(self):
        return f"<CartItem user={self.user_id} goods={self.goods_id} qty={self.quantity}>"


# ===================== 储值券 / 代金券 =====================
class Voucher(db.Model):
    """储值券，status='0' 未使用 / '1' 已使用。V-Race-Condition 漏洞场景相关。"""
    __tablename__ = "voucher"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False, unique=True)
    amount = db.Column(Numeric(10, 2), nullable=False)
    status = db.Column(db.String(1), default=VOUCHER_UNUSED)
    expires_at = db.Column(db.DateTime)
    used_at = db.Column(db.DateTime)
    used_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return f"<Voucher {self.code} ¥{self.amount}>"


# ===================== 订单主表 =====================
class Order(db.Model):
    """
    订单主表。
    - id: UUID 去横线后的 32 位字符串
    - payment_status: pending → paid → shipped → completed / cancelled
    - V-IDOR-View 漏洞：支付接口未校验订单归属
    """
    __tablename__ = "order"
    id = db.Column(db.String(32), primary_key=True, unique=True)
    order_number = db.Column(db.String(64), nullable=False, unique=True)
    generatetime = db.Column(db.DateTime)
    payment_status = db.Column(Enum('pending', 'paid', 'shipped', 'completed', 'cancelled', name='payment_status'), default='pending', nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(Numeric(10, 2), nullable=False, default=0.0)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))
    address_id = db.Column(db.Integer, db.ForeignKey('address.id'))
    paid_at = db.Column(db.DateTime)
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return f"<Order {self.order_number}>"


# ===================== 订单明细行 =====================
class OrderItem(db.Model):
    """订单中的单个商品行，记录下单时的快照价格和数量。"""
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(32), db.ForeignKey('order.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(Numeric(10, 2), nullable=False)
    subtotal = db.Column(Numeric(10, 2), nullable=False)
    order = db.relationship('Order', back_populates='items')
    goods = db.relationship('Goods', back_populates='order_items')
