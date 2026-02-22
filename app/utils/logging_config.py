"""
日志初始化模块。

调用 init_logging() 后会为根 Logger 同时添加：
- 控制台输出（StreamHandler）
- 文件轮转输出（RotatingFileHandler，单文件 5 MB，保留 5 份）

日志级别通过环境变量 LOG_LEVEL 控制，默认 INFO。
"""

import logging
import os
from logging.handlers import RotatingFileHandler


def init_logging() -> None:
    """初始化全局日志系统，在应用启动时调用一次。"""
    # 从环境变量读取日志级别，默认 INFO
    level_name = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, level_name, logging.INFO)

    # 统一日志格式：时间 级别 模块名 - 消息
    fmt = logging.Formatter("%(asctime)s %(levelname)s %(name)s - %(message)s")

    root = logging.getLogger()
    # 防止多次调用时重复添加 handler（如测试、热重载场景）
    if root.handlers:
        return
    root.setLevel(level)

    # 控制台处理器：输出到 stdout，便于 docker logs 查看
    console = logging.StreamHandler()
    console.setLevel(level)
    console.setFormatter(fmt)
    root.addHandler(console)

    # 文件轮转处理器：写入 logs/app.log，单文件 5 MB，保留 5 个备份
    log_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "logs")
    os.makedirs(log_dir, exist_ok=True)
    log_file = os.path.join(log_dir, "app.log")

    file_handler = RotatingFileHandler(log_file, maxBytes=5 * 1024 * 1024, backupCount=5, encoding="utf-8")
    file_handler.setLevel(level)
    file_handler.setFormatter(fmt)
    root.addHandler(file_handler)
