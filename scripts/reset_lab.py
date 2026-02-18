from app import app
from app.models.db import db

def reset():
    with app.app_context():
        db.drop_all()
        db.create_all()
        db.session.commit()
        print("Database reset complete")

if __name__ == "__main__":
    reset()