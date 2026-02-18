import os
import redis


def _get_env(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v else default


redis_client = redis.Redis(
    host=_get_env("REDIS_HOST", "127.0.0.1"),
    port=int(_get_env("REDIS_PORT", "6379")),
    db=int(_get_env("REDIS_DB", "0")),
    decode_responses=True,
)
