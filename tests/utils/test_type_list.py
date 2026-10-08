import pytest

from rudi_node_read.utils.type_list import (
    are_list_different,
    are_list_equal,
    check_is_list,
    check_is_list_or_none,
    clean_nones,
    ensure_is_str_list,
    get_first_list_elt_or_none,
    is_iterable,
    list_diff,
    merge_lists,
)


def test_is_iterable():
    assert is_iterable([])
    assert is_iterable("abc")
    assert not is_iterable(5)


def test_check_is_list():
    assert check_is_list([1]) == [1]
    with pytest.raises(TypeError):
        check_is_list("not a list")


def test_check_is_list_or_none():
    assert check_is_list_or_none(None) is None
    assert check_is_list_or_none([1]) == [1]
    with pytest.raises(TypeError):
        check_is_list_or_none("not a list")


def test_ensure_is_str_list():
    assert ensure_is_str_list(["a", "b"]) == ["a", "b"]
    assert ensure_is_str_list([" a ", "b "]) == ["a", "b"]
    assert ensure_is_str_list("a, b ,c") == ["a", "b", "c"]
    with pytest.raises(TypeError):
        ensure_is_str_list(5)  # type: ignore


def test_get_first_list_elt_or_none():
    assert get_first_list_elt_or_none([1, 2]) == 1
    assert get_first_list_elt_or_none([]) is None
    assert get_first_list_elt_or_none(None) is None
    assert get_first_list_elt_or_none("not a list") is None
    assert get_first_list_elt_or_none([None]) is None


def test_list_diff():
    assert list_diff([1, 2], [1, 2]) == []
    assert list_diff([1, 2], [2, 3]) == [1, 3]
    assert list_diff([], [1]) == [1]


def test_are_list_different():
    assert are_list_different([1], [1]) is False
    assert are_list_different([1, 2], [2, 1]) is False
    assert are_list_different([1], [2]) is True
    assert are_list_different(None, None) is False
    assert are_list_different(None, [1]) is True
    assert are_list_different([1], None) is True
    with pytest.raises(TypeError):
        are_list_different("a", [1])  # type: ignore


def test_are_list_equal():
    assert are_list_equal([1, 2], [2, 1])
    assert are_list_equal(None, None)
    assert not are_list_equal([1], [2])
    assert not are_list_equal([1], None)


def test_merge_lists():
    assert merge_lists([1], [2]) == [1, 2]
    assert merge_lists(None, [2]) == [2]
    assert merge_lists([1], None) == [1]
    assert merge_lists([1], 2) == [1, 2]
    assert merge_lists(1, [2]) == [1, 2]


def test_clean_nones():
    assert clean_nones([1, None, 2]) == [1, 2]
    assert clean_nones({"a": 1, "b": None}) == {"a": 1}
    assert clean_nones({"a": {"b": None, "c": 1}}) == {"a": {"c": 1}}
    assert clean_nones([{"a": None}, None]) == [{}]
    assert clean_nones("value") == "value"
