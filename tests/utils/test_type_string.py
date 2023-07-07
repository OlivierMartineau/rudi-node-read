import pytest

from rudi_node_read.utils.type_string import is_iso_full_date, is_string, is_uuid_v4, check_is_uuid4, slash_join


def test_is_string():
    assert is_string('e')
    assert not is_string(['e'])


def test_is_iso_full_date():
    assert is_iso_full_date('2019-05-02T11:30:57+00:00')
    assert is_iso_full_date('2019-05-02T11:30:57-10:00')
    assert is_iso_full_date('2019-05-02T11:30:57Z')


def test_is_uuid_v4():
    assert not is_uuid_v4(None)
    assert not is_uuid_v4('')
    assert not is_uuid_v4('1')
    assert not is_uuid_v4('1d8b8d5d5-82d4-4a93-96e8-451daa124a70')
    assert not is_uuid_v4('d8b8d5d5-82d4-1a93-96e8-451daa124a70')
    assert bool(is_uuid_v4('d8b8d5d5-82d4-4a93-96e8-451daa124a70'))


def test_validate_uuid_v4():
    with pytest.raises(ValueError):
        check_is_uuid4(None)
    with pytest.raises(ValueError):
        check_is_uuid4('')
    with pytest.raises(ValueError):
        check_is_uuid4('1')
    assert check_is_uuid4('d8b8d5d5-82d4-4a93-96e8-451daa124a70') == 'd8b8d5d5-82d4-4a93-96e8-451daa124a70'


def test_slash_join():
    assert slash_join('a', 'b', '4') == 'a/b/4'
    assert slash_join('a/', '/b', '/4/') == 'a/b/4'
    assert slash_join('/a//', '////b', '/4/') == 'a/b/4'
    assert slash_join('http://a//', '////b', '/4/') == 'http://a/b/4'
    assert slash_join('/', '////b', '/4/') == '/b/4'
    with pytest.raises(AttributeError):
        slash_join('a', 'b', 4)
