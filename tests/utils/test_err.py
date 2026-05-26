from typing import Literal

from rudi_node_read.utils.err import (
    MissingEnvironmentVariableException,
    IniMissingValueException,
    IniUnexpectedValueException,
    UnexpectedValueException,
    LiteralUnexpectedValueException,
    rudi_api_http_error_to_string,
)


def test_MissingEnvironmentVariableException():
    err = MissingEnvironmentVariableException("ENV_VAR", "for testing")
    target_err_msg = "an environment variable should be defined for testing: ENV_VAR"
    assert str(err) == target_err_msg
    try:
        raise err
    except MissingEnvironmentVariableException as e:
        assert str(e) == target_err_msg


def test_IniMissingValueException():
    err = IniMissingValueException("SECTION", "SUBSECTION", "testing")
    target_err_msg = "Missing value in INI config file for parameter SECTION.SUBSECTION: testing"
    assert str(err) == target_err_msg
    try:
        raise err
    except IniMissingValueException as e:
        assert str(e) == target_err_msg


def test_IniUnexpectedValueException():
    err = IniUnexpectedValueException("SECTION", "SUBSECTION", "testing")
    target_err_msg = "Unexpected value in INI config file for parameter SECTION.SUBSECTION: testing"
    assert str(err) == target_err_msg
    try:
        raise err
    except IniUnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_UnexpectedValueException():
    err = UnexpectedValueException("param", "val1", "val2")
    target_err_msg = "Unexpected value for parameter 'param': expected 'val1', got 'val2'"
    assert str(err) == target_err_msg
    try:
        raise err
    except UnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_ULiteralUnexpectedValueException():
    err = LiteralUnexpectedValueException("val", ("valA", "valB"), "error")
    target_err_msg = "error. Expected ('valA', 'valB'), got 'val'"
    assert str(err) == target_err_msg
    try:
        raise err
    except LiteralUnexpectedValueException as e:
        assert str(e) == target_err_msg


def test_rudi_api_http_error_to_string():
    assert rudi_api_http_error_to_string(444, "TestError", "testing err msg") == "ERR 444 TestError: testing err msg"
