from datetime import datetime
from app import app
from app.models.db import db, Admin, User, Goods

def seed():
    with app.app_context():
        if not Admin.query.first():
            db.session.add(Admin(username="admin", password="admin123"))

        if not User.query.first():
            db.session.add(User(username="alice", email="alice@test.com", password="alice123", balance=9999))

        if not Goods.query.first():
            db.session.add(Goods(goodsname="Demo Product", category="lab", price=99.9, stock=100, status="0",
                                mainimg="/static/img/default.jpg", content="seed demo"))

        db.session.commit()
        print("Seed complete: admin/admin123, alice/alice123")

if __name__ == "__main__":
    seed()