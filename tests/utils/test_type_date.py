from datetime import datetime

import pytest

from rudi_node_read.utils.type_date import Date


def test_date_from_none_uses_now():
    date = Date(None)
    assert date.year == datetime.now().year
    assert date.iso


def test_date_from_int():
    assert str(Date(20200101)) == "2020-01-01T00:00:00+00:00"
    assert Date(2020) == "2020"


def test_date_from_invalid_str():
    with pytest.raises(ValueError):
        Date("not a date")


def test_class_name():
    assert Date("2020").class_name == "Date"


def test_str():
    assert str(Date("2020-01-01T10:20:30Z")) == "2020-01-01T10:20:30+00:00"
    assert str(Date("2020-01-01T10:20:30+02:00")) == "2020-01-01T10:20:30+02:00"


def test_eq():
    assert Date("2020-01-01") == Date("2020-01-01T00:00:00")
    assert Date("2020-01-01") == "2020-01-01"
    assert Date("20200101") == 20200101
    assert not Date("2020-01-01") == 2.5
    assert Date("2020-01-01") is not None


def test_gt_lt():
    assert Date("2021-01-01") > Date("2020-01-01")
    assert Date("2021-01-01") > "2020-01-01"
    assert Date("2021-01-01") > 20200101
    assert Date("2020-01-01") < Date("2021-01-01")
    with pytest.raises(TypeError):
        assert Date("2020-01-01") > []


def test_to_json():
    date = Date("2020-01-01T10:20:30Z")
    assert date.to_json() == "2020-01-01T10:20:30+00:00"
    assert date.to_json_str() == "2020-01-01T10:20:30+00:00"


def test_from_str():
    assert Date.from_str("2020-01-01") == Date("2020-01-01")
    assert Date.from_str(None, default_date="2020-01-01") == Date("2020-01-01")
    assert Date.from_str(None) is None
    with pytest.raises(ValueError):
        Date.from_str(None, is_none_accepted=False)


def test_from_json():
    assert Date.from_json("2020-01-01") == Date("2020-01-01")
    assert Date.from_json(None) is None


def test_time_epochs():
    assert abs(Date.time_epoch_s() - datetime.now().timestamp()) < 5
    assert Date.time_epoch_s(delay_s=60) - Date.time_epoch_s() in range(55, 66)
    assert abs(Date.time_epoch_ms() - 1000 * datetime.now().timestamp()) < 5000
    assert Date.time_epoch_ms(delay_ms=1000) - Date.time_epoch_ms() in range(995, 1006)


def test_now():
    assert Date.now().year == datetime.now().year
    assert len(Date.now_str()) == len("2026-10-08 12:34:56")
    assert Date.now_iso().year == datetime.now().year


def test_is_iso_full_date_str():
    assert Date.is_iso_full_date_str("2019-05-02T11:30:57+00:00")
    assert Date.is_iso_full_date_str("2019-05-02T11:30:57.123Z")
    assert not Date.is_iso_full_date_str("2019-05-02 11:30:57")


def test_is_date_str():
    assert Date.is_date_str("2020-01-01")
    assert Date.is_date_str("2020")
    assert not Date.is_date_str("not a date")
