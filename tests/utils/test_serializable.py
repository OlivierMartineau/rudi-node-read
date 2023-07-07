from rudi_node_read.utils.serializable import Serializable


def test_to_json():
    assert Serializable().to_json() == '{}'


def test_str():
    assert str(Serializable()) == '{}'


def test_from_json_str():
    assert Serializable.from_json_str('{"arg1":"val1","arg2":"val2"}') == {'arg1': 'val1', 'arg2': 'val2'}
