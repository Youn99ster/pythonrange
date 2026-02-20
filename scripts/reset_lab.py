import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

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
