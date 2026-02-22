"""
HackShop 全局配置模块。

所有配置项优先读取环境变量，未设置时使用默认值。
容器部署时由 docker-compose.yml 注入环境变量覆盖默认值。
"""

import os
from datetime import timedelta


class Config:
    """Flask 应用配置类，通过 app.config.from_object(Config) 加载。"""

    # ---- 数据库（MySQL）连接 ----
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://"
        f"{os.getenv('MYSQL_USER', 'hackshop_user')}:"
        f"{os.getenv('MYSQL_PASSWORD', 'hackshop_password')}@"
        f"{os.getenv('MYSQL_HOST', '127.0.0.1')}:"
        f"{os.getenv('MYSQL_PORT', '3306')}/"
        f"{os.getenv('MYSQL_DB', 'hackshop_db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False  # 关闭事件通知，减少内存开销
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,   # 每次取连接前发送 ping，自动剔除断开的连接
        "pool_recycle": 1800,    # 连接最大存活 30 分钟，防止 MySQL wait_timeout 断连
        # 连接池参数可通过环境变量调优，避免高并发下频繁建连。
        "pool_size": int(os.getenv("DB_POOL_SIZE", "10")),
        "max_overflow": int(os.getenv("DB_MAX_OVERFLOW", "20")),
        "pool_timeout": int(os.getenv("DB_POOL_TIMEOUT", "30")),
    }

    # ---- Session / CSRF ----
    WTF_CSRF_ENABLED = False  # 靶场故意关闭 CSRF 保护，用于 V-CSRF-Pay 漏洞演示
    SECRET_KEY = os.getenv("SECRET_KEY", "hackshop-secret-key")  # Session 签名密钥
    PERMANENT_SESSION_LIFETIME = timedelta(days=7)  # "记住我" 有效期

    # ---- AES 加密配置（V-Admin-AES 漏洞） ----
    # 前端硬编码相同密钥对管理员密码进行 AES-CBC 加密后传输，
    # 服务端使用此处密钥解密。靶场故意暴露密钥以演示弱加密风险。
    AES_KEY = "HackShopAdminKey"   # 16 字节 AES 密钥
    AES_IV = "1234567890123456"    # 16 字节初始化向量
