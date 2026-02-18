import os


from datetime import timedelta


class Config:
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('MYSQL_USER', 'hackshop_user')}:"
        f"{os.getenv('MYSQL_PASSWORD', 'hackshop_password')}@"
        f"{os.getenv('MYSQL_HOST', '127.0.0.1')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DB', 'hackshop_db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 1800,
    }
    WTF_CSRF_ENABLED = False
    SECRET_KEY = os.getenv("SECRET_KEY", "hackshop-secret-key")
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)
    
    # AES Configuration for Admin Login (V-Admin-AES Vulnerability)
    # Hardcoded values matching frontend implementation
    AES_KEY = "HackShopAdminKey"
    AES_IV = "1234567890123456"


def get_database_uri() -> str:
    return Config.SQLALCHEMY_DATABASE_URI
