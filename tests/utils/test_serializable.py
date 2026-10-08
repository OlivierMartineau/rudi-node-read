# pyright: ignore

import unittest
from unittest.mock import patch

import pytest

from rudi_node_read.utils.serializable import Serializable, is_jsonable, is_serializable


def test_is_jsonable():
    assert is_jsonable({"field_1": "a_field"})


class Test_Serializable(unittest.TestCase):
    def test_from_json(self):
        with pytest.raises(NotImplementedError):
            Serializable.from_json({})  # type: ignore

    # https://stackoverflow.com/a/28738073/1563072
    @patch.multiple(Serializable, __abstractmethods__=set())
    def test(self):
        self.instance = Serializable()  # type: ignore
        self.instance.field_1 = "a_field"  # type: ignore
        other = Serializable()  # type: ignore
        other.field_1 = "a_field"  # type: ignore
        assert not is_jsonable(other)
        assert self.instance.to_json() == {"field_1": "a_field"}
        assert self.instance.to_json_str() == '{"field_1": "a_field"}'
        assert is_serializable(self.instance)
        # assert is_jsonable(self.instance)
        assert self.instance.class_name == "Serializable"
        assert self.instance is not None
        # direct call: `== None` would trip ruff E711, `!= None` would test __ne__
        assert self.instance.__eq__(None) is False
        assert self.instance != "None"
        assert self.instance != 0
        assert self.instance == other
        other.field_1 = "b_field"  # type: ignore
        assert self.instance != other
        other.field_1 = "a_field"  # type: ignore
        other.field_2 = "b_field"  # type: ignore
        assert self.instance != other
        other.field_1 = None  # type: ignore
        assert self.instance != other
        assert str(self.instance) == '{"field_1": "a_field"}'
        assert repr(self.instance) == '{"field_1": "a_field"}'

        assert other.to_json_str(keep_nones=True) == '{"field_1": null, "field_2": "b_field"}'

        self.instance.other = other  # type: ignore
        self.instance.a_dict = {"2": "str"}  # type: ignore
        self.instance.a_list = [1, 2]  # type: ignore
        assert (
            self.instance.to_json_str() == '{"field_1": "a_field", "other": {"field_2": "b_field"}, "a_dict": {'
            '"2": "str"}, "a_list": [1, 2]}'
        )

        assert self.instance.to_json() == {
            "field_1": "a_field",
            "other": {"field_2": "b_field"},
            "a_dict": {"2": "str"},
            "a_list": [1, 2],
        }


class SerializableList(list, Serializable):
    """A `Serializable` that is also a list: exercises the list branch of `to_json`."""

    @staticmethod
    def from_json(o):
        return SerializableList(o)


class FixedJson(Serializable):
    """A `Serializable` whose `to_json` returns a canned value, to exercise `__eq__`."""

    def __init__(self, json_value):
        self._json_value = json_value

    def to_json(self, keep_nones: bool = False):
        return self._json_value

    @staticmethod
    def from_json(o):
        return o


def test_to_json_on_a_list():
    assert SerializableList([1, 2, 3]).to_json() == [1, 2, 3]
    nested = SerializableList([1, SerializableList([2, 3])])
    assert nested.to_json() == [1, [2, 3]]


def test_eq_when_json_types_differ():
    assert FixedJson({"a": 1}) != FixedJson([1])
    assert FixedJson([1]) != FixedJson({"a": 1})


def test_eq_when_both_are_lists():
    assert FixedJson([1, 2]) == FixedJson([2, 1])
    assert FixedJson([1, 2]) != FixedJson([1, 3])
    assert FixedJson([]) == FixedJson([])


def test_eq_when_both_are_scalars():
    assert FixedJson("abc") == FixedJson("abc")
    assert FixedJson("abc") != FixedJson("abd")
    assert FixedJson(1) == FixedJson(1)
    assert FixedJson(1) != FixedJson(2)


def test_to_json_with_non_str_scalars():
    class Plain(Serializable):
        @staticmethod
        def from_json(o):
            return o

        def __init__(self):
            self.a_float = 1.5
            self.a_bool = False

    plain = Plain()
    assert plain.to_json() == {"a_float": 1.5, "a_bool": False}
