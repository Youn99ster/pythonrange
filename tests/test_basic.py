from app.controller.order import _generate_order_number, _parse_positive_int
from app.utils.tools import generate_orderid, generate_voucher_code, get_order_status_meta, unique_filename


def test_parse_positive_int_with_valid_value():
    assert _parse_positive_int("3") == 3


def test_parse_positive_int_with_invalid_value():
    assert _parse_positive_int("abc", default=2) == 2
    assert _parse_positive_int("-9", default=2) == 2


def test_generated_ids_are_non_empty_and_distinct():
    order_id = generate_orderid()
    voucher_code = generate_voucher_code()
    assert isinstance(order_id, str) and order_id
    assert isinstance(voucher_code, str) and voucher_code
    assert order_id != voucher_code


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
