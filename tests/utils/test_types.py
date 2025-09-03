import pytest

from rudi_node_read.utils.type_misc import (
    check_type,
    get_type_name,
    is_type,
    to_float,
)


def test_get_type_name():
    assert get_type_name({"arg": "val"}) == "dict"


def test_is_type():
    assert is_type({"arg": "val"}, "dict")
    assert is_type(["e"], "list")
    assert is_type("e", "str")
    assert is_type(1, "int")


def test_check_type():
    assert check_type(["sr"], "list") is None
    with pytest.raises(TypeError):
        check_type("str", "list")


def test_to_float():
    assert to_float("3") == 3.0
    assert to_float("3.0") == 3
    with pytest.raises(ValueError):
        to_float("str")
    with pytest.raises(ValueError):
        to_float(["4"])
