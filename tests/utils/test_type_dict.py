import pytest

from rudi_node_read.utils.type_dict import (
    check_has_key,
    filter_dict_list,
    find_in_dict_list,
    has_key,
    is_element_matching_filter,
    is_element_matching_one_of_filters,
    pick_in_dict,
    safe_get_key,
)


def test_has_key():
    assert has_key({"key": "val"}, "key")
    assert not has_key({"key": "val"}, "a")
    assert not has_key("key", "a")


def test_check_has_key():
    assert check_has_key({"arg": "val"}, "arg") == "val"
    with pytest.raises(AttributeError):
        check_has_key({"arg": "val"}, "val")


def test_safe_get_key():
    assert safe_get_key("er") is None
    assert safe_get_key({"arg": "val"}) is None
    assert safe_get_key({"arg": "val"}, "arg") == "val"
    assert safe_get_key({"lvl1": {"lvl2": "val"}}, "lvl1") == {"lvl2": "val"}
    assert safe_get_key({"lvl1": {"lvl2": "val"}}, "lvl1", "lvl2") == "val"
    assert safe_get_key({"lvl1": {"lvl2": {"lvl3": "val"}}}, "lvl1", "lvl2", "lvl3") == "val"
    assert safe_get_key({"lvl1": {"lvl2": {"lvl3": "val"}}}, "lvl1", "lvl2", "lvl3", "lvl4") is None


def test_pick_in_dict():
    assert pick_in_dict({"key1": "val1", "key2": "val2"}, ["key1"]) == {"key1": "val1"}
    assert pick_in_dict({"key1": "val1", "key2": "val2"}, ["key3"]) == {}
    a_dict = {"key1": "val1", "key2": "val2", "key3": "val3"}
    assert pick_in_dict(a_dict, ["key1", "key3"]) == {"key1": "val1", "key3": "val3"}


def test_is_element_matching_filter():
    list_a = ["1", "4", "5"]
    assert is_element_matching_filter(list_a, "1")
    assert is_element_matching_filter(list_a, ["1", "5"])
    assert not is_element_matching_filter(list_a, "2")
    assert not is_element_matching_filter(list_a, ["1", "2"])

    obj_a = {"a": "val1", "b": "val2", "c": "val3"}
    obj_b = {"d": "val4", "e": "val5", "f": "val6"}
    list_b = [obj_a, obj_b]
    assert is_element_matching_filter(obj_a, {"a": "val1", "b": "val2"})
    assert not is_element_matching_filter(obj_a, "a")
    assert not is_element_matching_filter(obj_a, {"a": "val1", "bb": "val2"})
    assert not is_element_matching_filter(obj_b, {"a": "val1", "b": "val2"})
    assert is_element_matching_filter(list_b, {"a": "val1", "b": "val2"})
    assert is_element_matching_filter(list_b, {"a": "val1", "b": "val2"})
    assert is_element_matching_filter({"x": list_b}, {"x": {"a": "val1", "b": "val2"}})
    assert is_element_matching_filter({"x": [list_b]}, {"x": {"a": "val1", "b": "val2"}})
    assert is_element_matching_filter({"x": obj_a}, {"x": {"a": "val1", "b": "val2"}})
    assert not is_element_matching_filter({"x": obj_b}, {"x": {"a": "val1", "b": "val2"}})
    assert is_element_matching_filter({"x": [obj_a]}, {"x": {"a": "val1", "b": "val2"}})
    assert is_element_matching_filter({"x": [obj_a, obj_b]}, {"x": {"a": "val1", "b": "val2"}})
    assert is_element_matching_filter({"x": [obj_b, list_b]}, {"x": {"a": "val1", "b": "val2"}})
    assert not is_element_matching_filter({"x": list_b}, {"y": {"a": "val1", "b": "val2"}})
    assert not is_element_matching_filter({"x": [list_b]}, {"y": {"a": "val1", "b": "val2"}})


def test_is_element_matching_one_of_filters():
    obj_a = {"a": "val1", "b": "val2", "c": "val3"}
    obj_b = {"d": "val4", "e": "val5", "f": "val6"}
    list_a = ["1", "4", "5"]
    list_b = [obj_a, obj_b]
    assert is_element_matching_one_of_filters(list_a, ["1", "2"])
    assert is_element_matching_one_of_filters([list_a, list_b], [obj_a, "2"])
    assert not is_element_matching_one_of_filters([list_a, list_b], ["g", "2"])


def test_filter_dict_list():
    obj_a = {"a": "val1", "b": "val2", "c": "val3", "f": "val6"}
    obj_b = {"d": "val4", "e": "val5", "f": "val6"}
    list_o = [obj_a, obj_b]
    assert filter_dict_list(list_o, obj_a) == [obj_a]
    assert filter_dict_list(list_o, {"a": "val1"}) == [obj_a]
    assert filter_dict_list(list_o, {"f": "val6"}) == list_o
    assert filter_dict_list(list_o, [{"f": "val6"}]) == list_o
    assert filter_dict_list(list_o, {"f": "val3"}) == []


def test_find_in_dict_list():
    obj_a = {"a": "val1", "b": "val2", "c": "val3", "f": "val6"}
    obj_b = {"d": "val4", "e": "val5", "f": "val6"}
    list_o = [obj_a, obj_b]
    assert find_in_dict_list(list_o, {"a": "val1"}) == obj_a
    assert find_in_dict_list(list_o, {"f": "val6"}) == obj_a
    assert find_in_dict_list(list_o, {"a": "val6"}) is None
