"""
HackShop 应用工厂入口模块。

职责：
1. 提供 create_app() 工厂函数，便于测试和多实例场景
2. 创建 Flask 应用实例并加载配置
3. 初始化日志系统（控制台 + 文件轮转）
4. 绑定 SQLAlchemy ORM 与 Flask-Migrate 数据库迁移
5. 注册各业务蓝图（前台、认证、订单、用户中心、管理后台）
"""

from flask import Flask
from flask_migrate import Migrate
from app.config import Config
from app.models.db import db
from app.utils.logging_config import init_logging


def create_app(config_class=Config):
    """应用工厂：创建并配置 Flask 实例。"""
    application = Flask(__name__, template_folder='./template/', static_folder='./static/')
    application.config.from_object(config_class)
    init_logging()
    db.init_app(application)
    Migrate(application, db)

    from app.controller.main import main_bp
    from app.controller.auth import auth_bp
    from app.controller.order import order_bp
    from app.controller.user import user_bp
    from app.controller.admin import admin_bp

    application.register_blueprint(main_bp)
    application.register_blueprint(auth_bp)
    application.register_blueprint(order_bp)
    application.register_blueprint(user_bp)
    application.register_blueprint(admin_bp)

    return application


# 模块级实例：供 gunicorn (app:app)、脚本 (from app import app) 直接使用
app = create_app()
