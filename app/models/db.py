from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import Enum


db = SQLAlchemy()

user_goods = db.Table('user_goods',
                      db.Column('user_id',db.Integer,db.ForeignKey('user.id')),
                      db.Column('goods_id',db.Integer,db.ForeignKey('goods.id'))
)

class Admin(db.Model):
    __tablename__ = 'admin'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(256), nullable=False, unique=True)
    password = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    last_login = db.Column(db.DateTime)

    def __repr__(self):
        return f"<Admin {self.username}>"

class MailLog(db.Model):
    __tablename__ = 'mail_logs'
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(255), nullable=False)
    sender = db.Column(db.String(255), nullable=False)
    receiver = db.Column(db.String(255), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    is_read = db.Column(db.Boolean, default=False, nullable=False)

class User(db.Model):
    __tablename__ = "user"
    id = db.Column(db.Integer,primary_key=True)
    username = db.Column(db.String(256),nullable=False,unique=True)
    email = db.Column(db.String(100),nullable=False,unique=True)
    password = db.Column(db.String(256),nullable=False)
    balance = db.Column(db.Float)
    goods = db.relationship('Goods',secondary=user_goods,back_populates='users')
    orders = db.relationship('Order',backref='user')
    addresses = db.relationship('Address',backref='user')
    vouchers = db.relationship('Voucher',backref='user')

class Address(db.Model):
    __tablename__ = "address"
    id = db.Column(db.Integer,primary_key=True)
    receiver = db.Column(db.String(16),nullable=False)
    phone = db.Column(db.String(256),nullable=False)
    addressname = db.Column(db.String(256))
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    orders = db.relationship('Order',backref='address')


    def __repr__(self):
        return "(%s,%s,%s)" %(self.receiver,self.addressname,self.user_id)

class Goods(db.Model):
    __tablename__ = "goods"
    id = db.Column(db.Integer,primary_key=True)
    goodsname = db.Column(db.String(256),nullable=False)
    category = db.Column(db.String(256),nullable=False)
    mainimg = db.Column(db.String(1024),nullable=False)
    content = db.Column(db.Text,nullable=False)
    stock = db.Column(db.Integer,nullable=False)
    price = db.Column(db.Float,nullable=False)
    status = db.Column(db.String(1),default="0")
    brand = db.Column(db.String(128))
    model = db.Column(db.String(256))
    original_price = db.Column(db.Float)
    rating_avg = db.Column(db.Float, default=0.0, nullable=False)
    rating_count = db.Column(db.Integer, default=0, nullable=False)
    sales_count = db.Column(db.Integer, default=0, nullable=False)
    slug = db.Column(db.String(256), unique=True)
    users = db.relationship('User', secondary=user_goods, back_populates='goods')
    order_items = db.relationship('OrderItem', back_populates='goods')
    images = db.relationship('GoodsImage', back_populates='goods', cascade='all, delete-orphan')
    specs = db.relationship('GoodsSpec', back_populates='goods', cascade='all, delete-orphan')

    def __repr__(self):
        return "(%s,%s,%s,%d,%f)" % (self.goodsname, self.mainimg, self.category, self.stock, self.price)

class GoodsImage(db.Model):
    __tablename__ = "goods_images"
    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    url = db.Column(db.String(1024), nullable=False)
    is_main = db.Column(db.Boolean, default=False, nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    goods = db.relationship('Goods', back_populates='images')

    def __repr__(self):
        return "(%d,%s,%s,%d)" % (self.goods_id, self.url, str(self.is_main), self.sort_order)

class GoodsSpec(db.Model):
    __tablename__ = "goods_specs"
    id = db.Column(db.Integer, primary_key=True)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    name = db.Column(db.String(128), nullable=False)
    value = db.Column(db.String(512), nullable=False)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    goods = db.relationship('Goods', back_populates='specs')

    def __repr__(self):
        return "(%d,%s,%s)" % (self.goods_id, self.name, self.value)

class CartItem(db.Model):
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

class Voucher(db.Model):
    __tablename__ = "voucher"
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(64), nullable=False, unique=True)
    amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(1), default="0")
    expires_at = db.Column(db.DateTime)
    used_at = db.Column(db.DateTime)
    used_by = db.Column(db.Integer, db.ForeignKey('user.id'))
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)

    def __repr__(self):
        return "(%s,%f,%s)" %(self.code,self.amount,self.status)

class Order(db.Model):
    __tablename__ = "order"
    id = db.Column(db.String(32),primary_key=True,unique=True)
    order_number = db.Column(db.String(32),nullable=False,unique=True)
    generatetime = db.Column(db.DateTime)
    payment_status = db.Column(Enum('pending','paid','shipped','completed','cancelled', name='payment_status'), default='pending', nullable=False)
    payment_method = db.Column(db.String(20), nullable=False)
    total_amount = db.Column(db.Float, nullable=False, default=0.0)
    user_id = db.Column(db.Integer,db.ForeignKey('user.id'))
    address_id = db.Column(db.Integer,db.ForeignKey('address.id'))
    paid_at = db.Column(db.DateTime)
    items = db.relationship('OrderItem', back_populates='order', cascade='all, delete-orphan')

    def __repr__(self):
        return "(%s,%s,%s,%s)" %(self.generatetime,self.payment_status,self.user_id,self.order_number)

class OrderItem(db.Model):
    __tablename__ = 'order_items'
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.String(32), db.ForeignKey('order.id'), nullable=False)
    goods_id = db.Column(db.Integer, db.ForeignKey('goods.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Float, nullable=False)
    subtotal = db.Column(db.Float, nullable=False)
    order = db.relationship('Order', back_populates='items')
    goods = db.relationship('Goods', back_populates='order_items')
