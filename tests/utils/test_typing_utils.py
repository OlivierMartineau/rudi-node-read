import pytest

from rudi_node_read.utils.typing_utils import (
    are_same_type,
    check_is_bool,
    check_is_bool_or_none,
    check_is_def,
    check_is_int,
    check_is_int_or_none,
    check_type,
    check_type_or_null,
    does_inherit_from,
    ensure_is_int,
    ensure_is_int_or_none,
    ensure_is_number,
    get_type_name,
    is_bool,
    is_def,
    is_null,
    is_number,
    is_type,
    is_type_name,
    to_float,
    to_number,
)


def test_get_type_name():
    assert get_type_name({}) == "dict"
    assert get_type_name(None) == "NoneType"


def test_is_type_name():
    assert is_type_name("e", "str")
    assert not is_type_name("e", "int")


def test_is_type():
    assert is_type("e", str)
    assert is_type(1, (int, float))
    assert not is_type("e", int)


def test_are_same_type():
    assert are_same_type("a", "b")
    assert not are_same_type("a", 1)


def test_does_inherit_from():
    assert does_inherit_from("e", str)
    assert not does_inherit_from("e", int)


def test_is_bool():
    assert is_bool(True)
    assert not is_bool("true")


def test_check_is_bool():
    assert check_is_bool(True) is True
    with pytest.raises(TypeError):
        check_is_bool("true")  # type: ignore


def test_check_is_bool_or_none():
    assert check_is_bool_or_none(None) is None
    assert check_is_bool_or_none(False) is False
    with pytest.raises(TypeError):
        check_is_bool_or_none(1)  # type: ignore


def test_check_type():
    assert check_type([], list) == []
    assert check_type({}, (dict, list)) == {}
    with pytest.raises(ValueError):
        check_type(None, list)
    with pytest.raises(TypeError) as exc:
        check_type("not a list", list)
    assert "'list'" in str(exc.value)
    assert "'str'" in str(exc.value)
    with pytest.raises(TypeError) as exc:
        check_type("not a list", (dict, list))
    assert "'dict' | 'list'" in str(exc.value)


def test_check_type_or_null():
    assert check_type_or_null(None, list) is None
    assert check_type_or_null([1], list) == [1]
    with pytest.raises(TypeError):
        check_type_or_null("e", list)


def test_check_is_int():
    assert check_is_int(5) == 5
    assert check_is_int("5", accept_castable=True) == 5
    with pytest.raises(ValueError):
        check_is_int(None)
    with pytest.raises(TypeError):
        check_is_int(5.5)
    with pytest.raises(TypeError):
        check_is_int("5.5", accept_castable=True)


def test_check_is_int_or_none():
    assert check_is_int_or_none(None) is None
    assert check_is_int_or_none(5) == 5
    assert check_is_int_or_none("5", accept_castable=True) == 5
    with pytest.raises(TypeError):
        check_is_int_or_none(5.5)
    with pytest.raises(TypeError):
        check_is_int_or_none("5.5", accept_castable=True)


def test_ensure_is_int():
    assert ensure_is_int(5) == 5
    assert ensure_is_int("7") == 7
    with pytest.raises(ValueError):
        ensure_is_int(None)
    with pytest.raises(TypeError):
        ensure_is_int([1])


def test_ensure_is_int_or_none():
    assert ensure_is_int_or_none(None) is None
    assert ensure_is_int_or_none(5) == 5
    assert ensure_is_int_or_none("7") == 7
    with pytest.raises(TypeError):
        ensure_is_int_or_none([1])


def test_is_number():
    assert is_number(1)
    assert is_number(1.5)
    assert not is_number("1")


def test_ensure_is_number():
    assert ensure_is_number(1) == 1
    assert ensure_is_number(1.5) == 1.5
    assert ensure_is_number("5") == 5
    with pytest.raises(TypeError):
        ensure_is_number("not a number")


def test_to_number():
    assert to_number(1) == 1
    assert to_number(1.5) == 1.5
    assert to_number("5") == 5
    assert to_number("-5") == -5
    assert to_number("5.5") == 5.5
    assert to_number("1.5e3") == 1500.0
    with pytest.raises(TypeError):
        to_number("not a number")


def test_to_float():
    assert to_float(5) == 5.0
    with pytest.raises(ValueError):
        to_float("not a number")
    with pytest.raises(ValueError):
        to_float(["4"])


def test_is_def():
    assert is_def("val")
    assert is_def("val", strict=True)
    assert not is_def(None)
    assert not is_def([], strict=True)


def test_check_is_def():
    assert check_is_def("val") == "val"
    assert check_is_def("val", strict=True) == "val"
    with pytest.raises(ValueError):
        check_is_def(None)
    with pytest.raises(ValueError):
        check_is_def([], strict=True)


def test_is_null():
    assert is_null(None)
    assert is_null("")
    assert is_null([])
    assert is_null("null")
    assert is_null("None")
    assert not is_null("val")
    assert is_null(None, strict=True)
    assert not is_null(0, strict=True)
    assert not is_null(True, strict=True)
    assert is_null([], strict=True)
    assert not is_null("[]", strict=True)
    assert not is_null("{}", strict=True)
