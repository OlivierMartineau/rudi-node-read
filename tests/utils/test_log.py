import pytest

import rudi_node_read.utils.log as log_module
from rudi_node_read.utils.log import (
    decorator_timer,
    log,
    log_assert,
    log_d,
    log_d_if,
    log_e,
    log_i,
    now,
)


@pytest.fixture(autouse=True)
def enable_logging(monkeypatch):
    """`log()` is a no-op unless `SHOULD_LOG` is set: force it on for these tests."""
    monkeypatch.setattr(log_module, "SHOULD_LOG", True)


def test_now():
    assert len(now()) == len("2026-10-08 12:34:56")


def test_log_arity_branches():
    log()
    log("single argument")
    log_d("debug message")
    log_i("info message")
    log_e("error message")
    log_d("ctx", "message")


def test_log_with_payload():
    log_d("ctx", "message", "payload")
    log_d("ctx", "message", "payload", "and more")


def test_log_when_disabled(monkeypatch):
    monkeypatch.setattr(log_module, "SHOULD_LOG", False)
    log_d("this should not be printed")
    log_e("neither should this")


def test_log_d_if():
    log_d_if(True, "ctx", "message")
    log_d_if(False, "ctx", "message")


class UnreadablePayload:
    """
    Stands in for a payload that cannot be decoded on the first attempt: the
    `log` fallback branch converts it once more, which succeeds.
    """

    def __init__(self):
        self.conversions = 0

    def __str__(self):
        self.conversions += 1
        if self.conversions == 1:
            raise UnicodeDecodeError("utf-8", b"\xff", 0, 1, "invalid start byte")
        return "recovered"


def test_log_falls_back_when_payload_cannot_be_printed():
    payload = UnreadablePayload()
    log_d("ctx", "message", payload)
    assert payload.conversions == 2


def test_decorator_timer():
    @decorator_timer
    def add(a, b):
        return a + b

    result, duration = add(2, 3)
    assert result == 5
    assert duration >= 0


def test_log_assert():
    assert log_assert(True) == "OK"
    assert log_assert(False) == "!! KO !!"
    assert log_assert(True, "yes", "no") == "yes"
    assert log_assert(False, "yes", "no") == "no"
