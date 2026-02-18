from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.controller.main import main_bp
from app.controller.auth import auth_bp
from app.controller.order import order_bp
from app.controller.user import user_bp
from app.controller.admin import admin_bp
from app.models.db import db
from app.utils.logging_config import init_logging

app = Flask(__name__, template_folder='./template/', static_folder='./static/')
app.config.from_object(Config)
init_logging()
db.init_app(app)
migrate = Migrate(app, db)

app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(order_bp)
app.register_blueprint(user_bp)
app.register_blueprint(admin_bp)
