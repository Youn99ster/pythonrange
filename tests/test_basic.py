"""
HackShop 基础单元测试。

测试范围（不依赖数据库 / Redis）：
- _parse_positive_int: 数量参数解析与兜底
- generate_uuid_hex: ID 生成非空且不重复
- _generate_order_number: 同一用户高频调用不碰撞
- get_order_status_meta: 未知状态回退到默认值
- unique_filename: 保留原始文件扩展名

运行方式：pytest tests/test_basic.py
"""

from app.controller.order import _generate_order_number, _parse_positive_int
from app.utils.tools import generate_uuid_hex, get_order_status_meta, unique_filename


def test_parse_positive_int_with_valid_value():
    assert _parse_positive_int("3") == 3


def test_parse_positive_int_with_invalid_value():
    assert _parse_positive_int("abc", default=2) == 2
    assert _parse_positive_int("-9", default=2) == 2


def test_generated_ids_are_non_empty_and_distinct():
    id_a = generate_uuid_hex()
    id_b = generate_uuid_hex()
    assert isinstance(id_a, str) and id_a
    assert isinstance(id_b, str) and id_b
    assert id_a != id_b


def test_generate_order_number_should_be_unique():
    numbers = {_generate_order_number(1) for _ in range(100)}
    assert len(numbers) == 100


def test_get_order_status_meta_fallback():
    label, cls = get_order_status_meta("unknown")
    assert label == "待付款"
    assert cls == "pending"


def test_unique_filename_should_keep_extension():
    name = unique_filename("avatar.png")
    assert name.endswith(".png")
