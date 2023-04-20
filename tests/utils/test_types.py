import pytest

from rudi_node_read.utils.log import log_d, log_e
from rudi_node_read.utils.types import get_type_name, is_type, is_list, is_array, is_list_or_dict, check_type, to_float


def test_get_type_name():
    assert get_type_name({'arg': 'val'}) == 'dict'


def test_is_type():
    assert is_type({'arg': 'val'}, 'dict')
    assert is_type(['e'], 'list')
    assert is_type('e', 'str')
    assert is_type(1, 'int')


def test_is_list():
    assert is_list([3, 4, 'dfg'])
    assert not is_list(3)
    assert not is_list({'e': 3})
    assert not is_list('e')


def test_is_array():
    assert is_array(['obj'])


def test_is_list_or_dict():
    assert is_list_or_dict(['r4'])
    assert is_list_or_dict({'r4': 4})
    assert is_list_or_dict({'r4': [4]})


def test_check_type():
    assert check_type(['sr'], 'list') is None
    with pytest.raises(TypeError):
        check_type('str', 'list')


def test_to_float():
    assert to_float("3") == 3.0
    assert to_float("3.0") == 3
    with pytest.raises(ValueError):
        to_float('str')
    with pytest.raises(ValueError):
        to_float(['4'])
