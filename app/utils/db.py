"""
Redis 客户端初始化模块。

提供全局单例 redis_client，供以下场景使用：
- 登录防爆破（失败计数 + 临时锁定）
- 邮箱验证码存储与校验
- 密码重置令牌的临时存储
"""

import os
import redis


def _get_env(name: str, default: str) -> str:
    """读取环境变量，空字符串视为未设置，回退到默认值。"""
    v = os.getenv(name)
    return v if v else default


# 全局 Redis 客户端（decode_responses=True 使返回值自动解码为 str）
redis_client = redis.Redis(
    host=_get_env("REDIS_HOST", "127.0.0.1"),
    port=int(_get_env("REDIS_PORT", "6379")),
    db=int(_get_env("REDIS_DB", "0")),
    decode_responses=True,
)
